"""The VMI Ventilairsec integration."""
from __future__ import annotations

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
except ImportError:  # pragma: no cover - used in local unit tests
    HomeAssistant = object  # type: ignore[assignment]
    ConfigEntry = object  # type: ignore[assignment]

DOMAIN = "vmi_ventilairsec"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the VMI Ventilairsec integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"entry": entry}
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "select", "number"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "select", "number"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
