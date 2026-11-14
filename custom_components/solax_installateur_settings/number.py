"""Number entities for numeric installer settings."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolaxInstallerCoordinator
from .entity import SolaxInstallerEntity
from .settings import KIND_NUMBER, SETTINGS, InstallerSetting


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolaxInstallerCoordinator = entry.runtime_data
    async_add_entities(
        SolaxInstallerNumber(coordinator, s) for s in SETTINGS if s.kind == KIND_NUMBER
    )


class SolaxInstallerNumber(SolaxInstallerEntity, NumberEntity):
    """An installer setting with a numeric value."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: SolaxInstallerCoordinator, setting: InstallerSetting) -> None:
        super().__init__(coordinator, setting.key)
        self.setting = setting
        self._attr_native_min_value = setting.min_value
        self._attr_native_max_value = setting.max_value
        self._attr_native_step = setting.step
        self._attr_native_unit_of_measurement = setting.unit
        self._attr_icon = setting.icon

    @property
    def native_value(self) -> float | None:
        raw = (self.coordinator.data or {}).get("settings", {}).get(self.setting.key)
        return None if raw is None else self.setting.raw_to_native(raw)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_setting(self.setting, value)
