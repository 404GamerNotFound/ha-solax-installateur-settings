"""Home Assistant component to manage Solax inverter installer settings."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .api import SolaxInstallerClient
from .const import CONF_HOST, CONF_PASSWORD, DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solax installer integration from a config entry."""
    host: str = entry.data[CONF_HOST]
    password: str = entry.data[CONF_PASSWORD]

    client = SolaxInstallerClient(hass, host, password)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    async def async_set_installer_setting(call: ServiceCall) -> None:
        await client.async_set_parameter(call.data["setting"], call.data["value"])

    hass.services.async_register(
        DOMAIN,
        "set_installer_setting",
        async_set_installer_setting,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, "set_installer_setting")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
