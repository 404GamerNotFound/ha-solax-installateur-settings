"""Home Assistant component to manage Solax inverter installer settings."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

from .api import SolaxInstallerClient
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SETTING,
    CONF_VALUE,
    DOMAIN,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solax installer integration from a config entry."""
    host: str = entry.options.get(CONF_HOST, entry.data[CONF_HOST])
    password: str = entry.options.get(CONF_PASSWORD, entry.data[CONF_PASSWORD])

    client = SolaxInstallerClient(hass, host, password)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    if not hass.services.has_service(DOMAIN, "set_installer_setting"):

        async def async_set_installer_setting(call: ServiceCall) -> None:
            service_host: str | None = call.data.get(CONF_HOST)
            target_client: SolaxInstallerClient | None = None

            if service_host:
                for stored_client in hass.data[DOMAIN].values():
                    if stored_client.host == service_host:
                        target_client = stored_client
                        break
            elif len(hass.data[DOMAIN]) == 1:
                target_client = next(iter(hass.data[DOMAIN].values()))

            if target_client is None:
                raise ValueError("Unknown or ambiguous inverter host")

            await target_client.async_set_parameter(
                call.data[CONF_SETTING], call.data[CONF_VALUE]
            )

        hass.services.async_register(
            DOMAIN, "set_installer_setting", async_set_installer_setting
        )

    if not hass.services.has_service(DOMAIN, "get_installer_settings"):

        async def async_get_installer_settings(call: ServiceCall) -> dict:
            service_host: str | None = call.data.get(CONF_HOST)
            target_client: SolaxInstallerClient | None = None

            if service_host:
                for stored_client in hass.data[DOMAIN].values():
                    if stored_client.host == service_host:
                        target_client = stored_client
                        break
            elif len(hass.data[DOMAIN]) == 1:
                target_client = next(iter(hass.data[DOMAIN].values()))

            if target_client is None:
                raise ValueError("Unknown or ambiguous inverter host")

            return await target_client.async_get_all_settings()

        hass.services.async_register(
            DOMAIN,
            "get_installer_settings",
            async_get_installer_settings,
            supports_response=SupportsResponse.ONLY,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "set_installer_setting")
        hass.services.async_remove(DOMAIN, "get_installer_settings")

    return True
