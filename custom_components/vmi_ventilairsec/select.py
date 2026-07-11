"""Select entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([VmiModeSelect(entry.entry_id)])


class VmiModeSelect(SelectEntity):
    _attr_name = "VMI Mode"
    _attr_options = ["Standby", "Eco", "Std", "Confort"]

    def __init__(self, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_mode"

    @property
    def current_option(self) -> str | None:
        return "Std"
