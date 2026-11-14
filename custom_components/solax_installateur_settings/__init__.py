"""Manage SolaX inverter installer settings (password protected) via Modbus TCP."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ConfigEntryAuthFailed, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import InvalidPassword, SolaxInstallerClient
from .const import (
    CONF_CONFIRM,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RELOCK,
    CONF_SCAN_INTERVAL,
    CONF_SETTING,
    CONF_UNIT_ID,
    CONF_VALUE,
    CONF_VIEW_ONLY,
    DEFAULT_PORT,
    DEFAULT_RELOCK,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DEFAULT_VIEW_ONLY,
    DOMAIN,
    SERVICE_GET,
    SERVICE_SET,
    SERVICE_UNLOCK,
)
from .coordinator import SolaxInstallerCoordinator
from .settings import find_setting

PLATFORMS = [Platform.BUTTON, Platform.NUMBER, Platform.SELECT, Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

TARGET_SCHEMA = {vol.Optional(CONF_HOST): cv.string}
SET_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SETTING): cv.string,
        vol.Required(CONF_VALUE): vol.Any(vol.Coerce(float), cv.string),
        vol.Required(CONF_CONFIRM): cv.boolean,
        **TARGET_SCHEMA,
    }
)
TARGET_ONLY_SCHEMA = vol.Schema(TARGET_SCHEMA)


def _target(hass: HomeAssistant, call: ServiceCall) -> SolaxInstallerCoordinator:
    coordinators: list[SolaxInstallerCoordinator] = [
        entry.runtime_data
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
    ]
    host = call.data.get(CONF_HOST)
    if host:
        coordinators = [c for c in coordinators if c.client.host == host]
    if len(coordinators) != 1:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="unknown_host"
        )
    return coordinators[0]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the integration services."""

    async def set_setting(call: ServiceCall) -> ServiceResponse:
        if not call.data[CONF_CONFIRM]:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="confirm_required"
            )
        coordinator = _target(hass, call)
        try:
            setting = find_setting(call.data[CONF_SETTING])
        except KeyError as err:
            raise ServiceValidationError(str(err)) from err
        value = call.data[CONF_VALUE]
        result = await coordinator.async_set_setting(setting, value)
        return {"setting": setting.name, "value": result}

    async def get_settings(call: ServiceCall) -> ServiceResponse:
        coordinator = _target(hass, call)
        return await coordinator.client.async_get_all_settings()

    async def unlock(call: ServiceCall) -> ServiceResponse:
        coordinator = _target(hass, call)
        return {"lock_state": await coordinator.async_unlock()}

    hass.services.async_register(
        DOMAIN, SERVICE_SET, set_setting, SET_SCHEMA, SupportsResponse.OPTIONAL
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET, get_settings, TARGET_ONLY_SCHEMA, SupportsResponse.ONLY
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UNLOCK, unlock, TARGET_ONLY_SCHEMA, SupportsResponse.OPTIONAL
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    data = entry.data
    options = entry.options
    try:
        client = SolaxInstallerClient(
            data[CONF_HOST],
            data.get(CONF_PORT, DEFAULT_PORT),
            data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
            data[CONF_PASSWORD],
            view_only=options.get(CONF_VIEW_ONLY, DEFAULT_VIEW_ONLY),
            relock_after_write=options.get(CONF_RELOCK, DEFAULT_RELOCK),
        )
    except InvalidPassword as err:
        raise ConfigEntryAuthFailed(str(err)) from err

    coordinator = SolaxInstallerCoordinator(
        hass, entry, client, options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate v1 entries (HTTP API) to v2 (Modbus TCP)."""
    if entry.version == 1:
        host = str(entry.options.get(CONF_HOST, entry.data.get(CONF_HOST, "")))
        parsed = urlparse(host if "://" in host else f"//{host}")
        new_data = {
            CONF_HOST: parsed.hostname or host,
            CONF_PORT: DEFAULT_PORT,
            CONF_UNIT_ID: DEFAULT_UNIT_ID,
            CONF_PASSWORD: entry.options.get(
                CONF_PASSWORD, entry.data.get(CONF_PASSWORD, "")
            ),
        }
        new_options = {
            CONF_VIEW_ONLY: entry.options.get(
                CONF_VIEW_ONLY, entry.data.get(CONF_VIEW_ONLY, DEFAULT_VIEW_ONLY)
            )
        }
        hass.config_entries.async_update_entry(
            entry, data=new_data, options=new_options, version=2
        )
    return True
