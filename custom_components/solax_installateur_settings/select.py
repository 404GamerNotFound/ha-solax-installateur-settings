"""Select entities for installer settings with fixed options."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolaxInstallerCoordinator
from .entity import SolaxInstallerEntity
from .settings import KIND_SELECT, SETTINGS, InstallerSetting, option_key


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolaxInstallerCoordinator = entry.runtime_data
    async_add_entities(
        SolaxInstallerSelect(coordinator, s) for s in SETTINGS if s.kind == KIND_SELECT
    )


class SolaxInstallerSelect(SolaxInstallerEntity, SelectEntity):
    """An installer setting with a list of options."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SolaxInstallerCoordinator, setting: InstallerSetting) -> None:
        super().__init__(coordinator, setting.key)
        self.setting = setting
        self._raw_by_option = {option_key(label): raw for raw, label in setting.options.items()}
        self._attr_options = list(self._raw_by_option)
        self._attr_icon = setting.icon

    @property
    def current_option(self) -> str | None:
        raw = (self.coordinator.data or {}).get("settings", {}).get(self.setting.key)
        label = self.setting.options.get(raw) if raw is not None else None
        return option_key(label) if label else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_setting(self.setting, self._raw_by_option[option])
