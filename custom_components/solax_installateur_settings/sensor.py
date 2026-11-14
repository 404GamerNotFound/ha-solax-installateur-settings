"""Sensor showing the inverter lock state."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolaxInstallerCoordinator
from .entity import SolaxInstallerEntity
from .settings import LOCK_STATES


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([SolaxLockStateSensor(entry.runtime_data)])


class SolaxLockStateSensor(SolaxInstallerEntity, SensorEntity):
    """Current lock state reported by the inverter."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(LOCK_STATES.values())
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lock-question"

    def __init__(self, coordinator: SolaxInstallerCoordinator) -> None:
        super().__init__(coordinator, "lock_state")

    @property
    def native_value(self) -> str | None:
        raw = (self.coordinator.data or {}).get("lock_state")
        return LOCK_STATES.get(raw)
