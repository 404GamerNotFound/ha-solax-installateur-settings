"""Buttons to unlock (with the installer password) and lock the inverter."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolaxInstallerCoordinator
from .entity import SolaxInstallerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolaxInstallerCoordinator = entry.runtime_data
    async_add_entities([SolaxUnlockButton(coordinator), SolaxLockButton(coordinator)])


class SolaxUnlockButton(SolaxInstallerEntity, ButtonEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:lock-open-variant"

    def __init__(self, coordinator: SolaxInstallerCoordinator) -> None:
        super().__init__(coordinator, "unlock")

    async def async_press(self) -> None:
        await self.coordinator.async_unlock()


class SolaxLockButton(SolaxInstallerEntity, ButtonEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:lock"

    def __init__(self, coordinator: SolaxInstallerCoordinator) -> None:
        super().__init__(coordinator, "lock")

    async def async_press(self) -> None:
        await self.coordinator.async_lock()
