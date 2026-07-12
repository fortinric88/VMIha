"""The VMI Ventilairsec integration."""
from __future__ import annotations

import asyncio
from typing import Any

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
except ImportError:  # pragma: no cover - used in local unit tests
    HomeAssistant = object  # type: ignore[assignment]
    ConfigEntry = object  # type: ignore[assignment]

from .enocean_listener import EnOceanSerialListener

DOMAIN = "vmi_ventilairsec"


def get_device_specs() -> list[dict[str, Any]]:
    """Return the device layout described in the Ventilairsec plugin backup."""
    return [
        {
            "name": "CO2 Sensor",
            "manufacturer": "VMI",
            "model": "EEP A5-09-04",
            "address": "0x81003227",
            "sensors": [
                {"key": "co2", "name": "CO2", "unit": "ppm", "device_class": "carbon_dioxide"},
                {"key": "temperature", "name": "Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "humidity", "name": "Humidity", "unit": "%", "device_class": "humidity"},
            ],
            "selects": [],
            "numbers": [],
        },
        {
            "name": "Temperature/Humidity Sensor",
            "manufacturer": "VMI",
            "model": "EEP A5-04-01",
            "address": "0x810054F5",
            "sensors": [
                {"key": "temperature", "name": "Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "humidity", "name": "Humidity", "unit": "%", "device_class": "humidity"},
            ],
            "selects": [],
            "numbers": [],
        },
        {
            "name": "VMI Purevent",
            "manufacturer": "VMI",
            "model": "EEP D1079-01-00",
            "address": "0x0421574F",
            "sensors": [
                {"key": "mode", "name": "Mode", "unit": None, "device_class": None},
                {"key": "upstream_temperature", "name": "Upstream Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "downstream_temperature", "name": "Downstream Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "heating_setpoint", "name": "Heating Setpoint", "unit": "°C", "device_class": "temperature"},
            ],
            "selects": [
                {"key": "mode", "name": "Ventilation Mode"},
            ],
            "numbers": [
                {"key": "heating_setpoint", "name": "Heating Setpoint"},
            ],
        },
        {
            "name": "VMI Assistant Ventilairsec",
            "manufacturer": "VMI",
            "model": "EEP D1079-00-00",
            "address": "0x0422407D",
            "sensors": [
                {"key": "temperature", "name": "Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "humidity", "name": "Humidity", "unit": "%", "device_class": "humidity"},
            ],
            "selects": [],
            "numbers": [],
        },
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the VMI Ventilairsec integration from a config entry."""
    listener = EnOceanSerialListener(port=entry.options.get("serial_port", "/dev/ttyS2"))
    listener.start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"entry": entry, "listener": listener}
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "select", "number"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "select", "number"])
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data is not None and "listener" in data:
            data["listener"].stop()
    return unload_ok
