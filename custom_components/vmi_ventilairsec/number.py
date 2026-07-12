"""Number entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, get_device_specs


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entities: list[NumberEntity] = []
    for device in get_device_specs():
        for spec in device["numbers"]:
            entities.append(VmiDeviceNumber(entry.entry_id, device["name"], spec["key"], spec["name"]))
    async_add_entities(entities)


class VmiDeviceNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_native_min_value = 8
    _attr_native_max_value = 28
    _attr_native_step = 1

    def __init__(self, entry_id: str, device_name: str, key: str, name: str) -> None:
        device_slug = device_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{device_slug}_{key}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"vmi_{device_slug}")},
            "name": device_name,
            "manufacturer": "VMI",
            "model": device_name,
        }
        self.entity_id = f"number.{device_slug}_{key}"

    @property
    def native_value(self):
        return 20
