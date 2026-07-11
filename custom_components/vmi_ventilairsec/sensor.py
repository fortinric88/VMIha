"""Sensor entities for VMI Ventilairsec."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([
        VmiTemperatureSensor(entry.entry_id),
        VmiHumiditySensor(entry.entry_id),
        VmiCo2Sensor(entry.entry_id),
    ])


class VmiTemperatureSensor(SensorEntity):
    _attr_name = "VMI Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"

    def __init__(self, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_temperature"

    @property
    def native_value(self):
        return 22.0


class VmiHumiditySensor(SensorEntity):
    _attr_name = "VMI Humidity"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_humidity"

    @property
    def native_value(self):
        return 50


class VmiCo2Sensor(SensorEntity):
    _attr_name = "VMI CO2"
    _attr_native_unit_of_measurement = "ppm"

    def __init__(self, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_co2"

    @property
    def native_value(self):
        return 450
