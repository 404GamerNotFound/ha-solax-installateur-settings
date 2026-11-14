"""Base entity for SolaX installer settings."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import SolaxInstallerCoordinator


class SolaxInstallerEntity(CoordinatorEntity[SolaxInstallerCoordinator]):
    """Common entity attributes."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SolaxInstallerCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        base = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{base}_{key}"
        self._attr_translation_key = key
        serial = coordinator.client.serial
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, base)},
            name="SolaX Installer Settings",
            manufacturer=MANUFACTURER,
            serial_number=serial,
            configuration_url=None,
        )
