"""Config flow for the SolaX installer settings integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import InvalidPassword, SolaxInstallerClient
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RELOCK,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    CONF_VIEW_ONLY,
    DEFAULT_PORT,
    DEFAULT_RELOCK,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DEFAULT_VIEW_ONLY,
    DOMAIN,
)
from .modbus import ModbusError

_LOGGER = logging.getLogger(__name__)

PASSWORD_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def _connection_schema(defaults: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Required(
                CONF_UNIT_ID, default=defaults.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=247)),
            vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
        }
    )


async def _validate(data: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    errors: dict[str, str] = {}
    info: dict[str, Any] = {}
    try:
        client = SolaxInstallerClient(
            data[CONF_HOST], data[CONF_PORT], data[CONF_UNIT_ID], data[CONF_PASSWORD]
        )
        info = await client.async_validate()
    except InvalidPassword:
        errors["base"] = "invalid_auth"
    except ModbusError as err:
        _LOGGER.debug("Connection test failed: %s", err)
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Unexpected error during validation")
        errors["base"] = "unknown"
    return errors, info


class SolaxInstallerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            errors, info = await _validate(user_input)
            if not errors:
                serial = info.get("serial")
                await self.async_set_unique_id(
                    serial or f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                view_only = user_input.pop(CONF_VIEW_ONLY, DEFAULT_VIEW_ONLY)
                return self.async_create_entry(
                    title=f"SolaX {serial}" if serial else f"SolaX {user_input[CONF_HOST]}",
                    data=user_input,
                    options={CONF_VIEW_ONLY: view_only},
                )

        schema = _connection_schema(user_input or {}).extend(
            {vol.Required(CONF_VIEW_ONLY, default=DEFAULT_VIEW_ONLY): bool}
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
            errors, _ = await _validate(data)
            if not errors:
                return self.async_update_reload_and_abort(entry, data=data)
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            errors, info = await _validate(user_input)
            if not errors:
                if info.get("serial") and entry.unique_id != info["serial"]:
                    return self.async_abort(reason="wrong_device")
                return self.async_update_reload_and_abort(entry, data=user_input)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_connection_schema(user_input or entry.data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SolaxInstallerOptionsFlow()


class SolaxInstallerOptionsFlow(OptionsFlow):
    """Safety and polling options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return self.async_create_entry(data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_VIEW_ONLY, default=options.get(CONF_VIEW_ONLY, DEFAULT_VIEW_ONLY)
                    ): bool,
                    vol.Required(
                        CONF_RELOCK, default=options.get(CONF_RELOCK, DEFAULT_RELOCK)
                    ): bool,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=10, max=3600, step=1, unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )
