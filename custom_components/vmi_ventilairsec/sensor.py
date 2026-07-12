"""Sensor entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN, get_device_specs


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entities: list[SensorEntity] = []
    for device in get_device_specs():
        for spec in device["sensors"]:
            entities.append(
                VmiDeviceSensor(entry.entry_id, device["name"], spec["key"], spec["name"], spec["unit"], spec["device_class"])
            )
    async_add_entities(entities)


class VmiDeviceSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry_id: str, device_name: str, key: str, name: str, unit: str | None, device_class: str | None) -> None:
        self._key = key
        device_slug = device_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry_id}_{device_slug}_{key}"
        self._attr_name = name
        self._attr_translation_key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"vmi_{device_slug}")},
            "name": device_name,
            "manufacturer": "VMI",
            "model": device_name,
        }
        self._attr_should_poll = False
        self.entity_id = f"sensor.{device_slug}_{key}"

    @property
    def native_value(self):
        mapping = {
            "co2": 450,
            "temperature": 22.0,
            "humidity": 50,
            "mode": "Std",
            "upstream_temperature": 20.0,
            "downstream_temperature": 21.0,
            "heating_setpoint": 20.0,
        }
        return mapping.get(self._key, 0)
