"""Data update coordinator for SolaX installer settings."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import InvalidPassword, SolaxInstallerClient, ViewOnlyError
from .const import DOMAIN
from .modbus import ModbusError
from .settings import InstallerSetting

_LOGGER = logging.getLogger(__name__)


class SolaxInstallerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the installer settings and performs writes."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: SolaxInstallerClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_read_all()
        except ModbusError as err:
            raise UpdateFailed(f"Error communicating with inverter: {err}") from err

    def _handle_auth_error(self, err: InvalidPassword) -> HomeAssistantError:
        self.config_entry.async_start_reauth(self.hass)
        return HomeAssistantError(
            translation_domain=DOMAIN, translation_key="invalid_auth"
        )

    async def async_set_setting(self, setting: InstallerSetting | str, value: Any):
        try:
            result = await self.client.async_set_setting(setting, value)
        except ViewOnlyError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="view_only"
            ) from err
        except InvalidPassword as err:
            raise self._handle_auth_error(err) from err
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        await self.async_request_refresh()
        return result

    async def async_unlock(self) -> str:
        if self.client.view_only:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="view_only"
            )
        try:
            state = await self.client.async_unlock()
        except InvalidPassword as err:
            raise self._handle_auth_error(err) from err
        except ModbusError as err:
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()
        return state

    async def async_lock(self) -> str:
        try:
            state = await self.client.async_lock()
        except ModbusError as err:
            raise HomeAssistantError(str(err)) from err
        await self.async_request_refresh()
        return state
