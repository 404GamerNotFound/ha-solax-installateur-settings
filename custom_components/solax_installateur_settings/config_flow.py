"""Config flow for Solax installer integration."""

from __future__ import annotations

import asyncio

from aiohttp import ClientError
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SETTING,
    CONF_VALUE,
    CONF_VIEW_ONLY,
    DOMAIN,
    SETTING_NAMES,
)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Required(CONF_VIEW_ONLY, default=True): bool,
})


class SolaxInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the integration."""

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            client = SolaxInstallerClient(
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_PASSWORD],
                user_input[CONF_VIEW_ONLY],
            )
            try:
                await client.async_get_all_settings()
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Solax Installer", data=user_input)
            except (ClientError, asyncio.TimeoutError, ValueError):
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SolaxInstallerOptionsFlow(config_entry)


class SolaxInstallerOptionsFlow(config_entries.OptionsFlow):
    """Options flow to change settings after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors: dict[str, str] = {}

        host = self.config_entry.options.get(CONF_HOST, self.config_entry.data[CONF_HOST])
        password = self.config_entry.options.get(
            CONF_PASSWORD, self.config_entry.data[CONF_PASSWORD]
        )
        view_only = self.config_entry.options.get(
            CONF_VIEW_ONLY, self.config_entry.data.get(CONF_VIEW_ONLY, True)
        )

        if user_input is not None:
            host = user_input.get(CONF_HOST, host)
            password = user_input.get(CONF_PASSWORD, password)
            view_only = user_input.get(CONF_VIEW_ONLY, view_only)

        client = SolaxInstallerClient(self.hass, host, password, view_only)

        if user_input is not None:
            setting = user_input.pop(CONF_SETTING, None)
            value = user_input.pop(CONF_VALUE, None)
            if setting and value:
                try:
                    await client.async_set_parameter(setting, value)
                except PermissionError:
                    errors["base"] = "view_only"
                except (ClientError, asyncio.TimeoutError):
                    errors["base"] = "cannot_connect"
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        options = {}
        try:
            settings = await client.async_get_all_settings()
            if not isinstance(settings, dict):
                raise ValueError
            options = {
                f"{SETTING_NAMES.get(key, key)} ({value})": key
                for key, value in settings.items()
            }
        except (ClientError, asyncio.TimeoutError, ValueError):
            errors.setdefault("base", "cannot_connect")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=host,
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=password,
                    ): str,
                    vol.Required(
                        CONF_VIEW_ONLY,
                        default=view_only,
                    ): bool,
                    vol.Optional(CONF_SETTING): vol.In(options),
                    vol.Optional(CONF_VALUE): str,
                }
            ),
            errors=errors,
        )
