"""Number entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, VmiDataStore, get_device_specs


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data_store: VmiDataStore = hass.data[DOMAIN][entry.entry_id]["data_store"]
    entities: list[NumberEntity] = []
    for device in get_device_specs():
        for spec in device["numbers"]:
            entities.append(
                VmiDeviceNumber(entry.entry_id, device["name"], spec["key"], spec["name"], data_store)
            )
    async_add_entities(entities)


class VmiDeviceNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, entry_id: str, device_name: str, key: str, name: str, data_store: VmiDataStore) -> None:
        self._key = key
        self._device_slug = device_name.lower().replace(" ", "_").replace("/", "_")
        self._data_store = data_store
        self._attr_unique_id = f"{entry_id}_{self._device_slug}_{key}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"vmi_{self._device_slug}")},
            "name": device_name,
            "manufacturer": "VMI",
            "model": device_name,
        }

    async def async_added_to_hass(self) -> None:
        self._data_store.register_entity(self)

    async def async_will_remove_from_hass(self) -> None:
        self._data_store.unregister_entity(self)

    @property
    def device_slug(self) -> str:
        return self._device_slug

    @property
    def native_value(self):
        return self._data_store.data.get(self._device_slug, {}).get(self._key)

    @property
    def available(self) -> bool:
        return self._key in self._data_store.data.get(self._device_slug, {})
