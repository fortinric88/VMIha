"""The VMI Ventilairsec integration."""
from __future__ import annotations

import asyncio
import threading
from typing import Any

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
except ImportError:  # pragma: no cover - used in local unit tests
    HomeAssistant = object  # type: ignore[assignment]
    ConfigEntry = object  # type: ignore[assignment]

DOMAIN = "vmi_ventilairsec"

class VmiDataStore:
    """In-memory state for VMI device values."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.data: dict[str, dict[str, Any]] = {}
        self.entities: list[Any] = []
        self._lock = threading.Lock()

    def register_entity(self, entity: Any) -> None:
        with self._lock:
            self.entities.append(entity)

    def unregister_entity(self, entity: Any) -> None:
        with self._lock:
            if entity in self.entities:
                self.entities.remove(entity)

    def update_device(self, device_slug: str, values: dict[str, Any]) -> None:
        with self._lock:
            self.data.setdefault(device_slug, {}).update(values)
        self.hass.loop.call_soon_threadsafe(self._schedule_updates, device_slug)

    def _schedule_updates(self, device_slug: str) -> None:
        with self._lock:
            entities = list(self.entities)
        for entity in entities:
            if getattr(entity, "device_slug", None) == device_slug:
                entity.async_schedule_update_ha_state()

    def update_from_payload(self, payload_info: dict[str, Any]) -> None:
        device_slug = payload_info.get("device_slug", "vmi_purevent")
        parsed = payload_info.get("parsed", {})
        if not parsed:
            return
        self.update_device(device_slug, parsed)

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the VMI Ventilairsec component."""
    return True


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
                {"key": "bypass", "name": "Bypass Active", "unit": None, "device_class": None},
                {"key": "time_slot_active", "name": "Time Slot Active", "unit": None, "device_class": None},
                {"key": "debit_fixe", "name": "Fixed Flow", "unit": None, "device_class": None},
                {"key": "surventilation", "name": "Overventilation", "unit": None, "device_class": None},
                {"key": "vacances", "name": "Vacation Mode", "unit": None, "device_class": None},
                {"key": "season", "name": "Season", "unit": None, "device_class": None},
                {"key": "event_type", "name": "Event Type", "unit": None, "device_class": None},
                {"key": "boost_remaining", "name": "Boost Remaining", "unit": "minutes", "device_class": None},
                {"key": "setpoint_electric", "name": "Electric Setpoint", "unit": "°C", "device_class": "temperature"},
                {"key": "setpoint_max_soufflage", "name": "Max Fan Speed Setpoint", "unit": "RPM", "device_class": None},
                {"key": "setpoint_hydror", "name": "HydroR Setpoint", "unit": "°C", "device_class": "temperature"},
                {"key": "setpoint_solar", "name": "Solar Setpoint", "unit": "°C", "device_class": "temperature"},
            ],
            "selects": [
                {"key": "mode", "name": "Ventilation Mode"},
                {"key": "season", "name": "Season"},
            ],
            "numbers": [
                {"key": "boost_remaining", "name": "Boost Remaining"},
                {"key": "setpoint_electric", "name": "Electric Setpoint"},
                {"key": "setpoint_max_soufflage", "name": "Max Fan Speed Setpoint"},
                {"key": "setpoint_hydror", "name": "HydroR Setpoint"},
                {"key": "setpoint_solar", "name": "Solar Setpoint"},
            ],
        },
        {
            "name": "VMI Assistant Ventilairsec",
            "manufacturer": "VMI",
            "model": "EEP D1079-00-00",
            "address": "0x0422407D",
            "sensors": [
                {"key": "battery_level", "name": "Battery Level", "unit": None, "device_class": None},
                {"key": "temperature", "name": "Temperature", "unit": "°C", "device_class": "temperature"},
                {"key": "humidity", "name": "Humidity", "unit": "%", "device_class": "humidity"},
            ],
            "selects": [],
            "numbers": [],
        },
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the VMI Ventilairsec integration from a config entry."""
    # Import listener lazily to avoid raising import errors during package import
    try:
        from .enocean_listener import EnOceanSerialListener
    except Exception:
        EnOceanSerialListener = None  # type: ignore

    data_store = VmiDataStore(hass)
    listener = None
    if EnOceanSerialListener is not None:
        listener = EnOceanSerialListener(
            port=entry.options.get("serial_port", "/dev/ttyS2"),
            callback=data_store.update_from_payload,
        )
        listener.start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "entry": entry,
        "listener": listener,
        "data_store": data_store,
    }
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
