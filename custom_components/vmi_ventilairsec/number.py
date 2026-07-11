"""Number entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([VmiSetpointNumber(entry.entry_id)])


class VmiSetpointNumber(NumberEntity):
    _attr_name = "VMI Setpoint"
    _attr_native_min_value = 8
    _attr_native_max_value = 28
    _attr_native_step = 1

    def __init__(self, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_setpoint"

    @property
    def native_value(self):
        return 20
