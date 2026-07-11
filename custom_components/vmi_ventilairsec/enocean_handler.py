"""Helpers to decode the proprietary Ventilairsec EnOcean payloads."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def _extract_bits(value: int, offset: int, size: int) -> int:
    mask = (1 << size) - 1
    return (value >> offset) & mask


def _decode_mode(raw: int) -> str:
    mapping = {
        0: "Standby",
        1: "Eco",
        2: "Std",
        3: "Confort",
    }
    return mapping.get(raw, f"Unknown ({raw})")


def _decode_battery(raw: int) -> str:
    mapping = {
        0: "Off",
        1: "Level 0",
        2: "Level 1",
        3: "Level 2",
        4: "Level 3",
        5: "Level 4",
        6: "Level 5",
    }
    return mapping.get(raw, f"Unknown ({raw})")


def _decode_season(raw: int) -> str:
    mapping = {0: "Ete", 1: "Hiver", 2: "Intermediaire"}
    return mapping.get(raw, f"Unknown ({raw})")


def _decode_event_type(raw: int) -> str:
    return {0: "Periodic", 1: "Event"}.get(raw, f"Unknown ({raw})")


def parse_d1079_payload(payload: str, func: str, device_type: str) -> dict[str, Any]:
    """Parse the proprietary Ventilairsec MSC payloads.

    The original Jeedom backup exposes these payloads under the manufacturer-specific
    D1079 RORG. The XML definitions document the field offsets and sizes from the
    backup, so the parser maps those values into plain Python values.
    """

    if payload.startswith("0x"):
        payload = payload[2:]

    payload = payload.zfill(16)
    value = int(payload, 16)

    if func == "01" and device_type == "00":
        mode_raw = _extract_bits(value, 16, 8)
        bypass_raw = _extract_bits(value, 26, 1)
        time_slot_raw = _extract_bits(value, 27, 1)
        debit_fixe_raw = _extract_bits(value, 28, 1)
        survent_raw = _extract_bits(value, 30, 1)
        vac_raw = _extract_bits(value, 31, 1)
        boost_raw = _extract_bits(value, 32, 8)
        electric_raw = _extract_bits(value, 40, 8)
        max_soufflage_raw = _extract_bits(value, 48, 8)
        hydror_raw = _extract_bits(value, 56, 8)
        solar_raw = _extract_bits(value, 64, 8)
        season_raw = _extract_bits(value, 80, 8)
        event_raw = _extract_bits(value, 88, 8)

        return {
            "mode": _decode_mode(mode_raw),
            "mode_raw": mode_raw,
            "bypass": bool(bypass_raw),
            "time_slot_active": bool(time_slot_raw),
            "debit_fixe": bool(debit_fixe_raw),
            "surventilation": bool(survent_raw),
            "vacances": bool(vac_raw),
            "boost_remaining": boost_raw,
            "setpoint_electric": electric_raw,
            "setpoint_max_soufflage": max_soufflage_raw,
            "setpoint_hydror": hydror_raw,
            "setpoint_solar": solar_raw,
            "season": _decode_season(season_raw),
            "season_raw": season_raw,
            "event_type": _decode_event_type(event_raw),
            "event_type_raw": event_raw,
        }

    if func == "00" and device_type == "00":
        battery_raw = _extract_bits(value, 16, 8)
        temp_raw = _extract_bits(value, 24, 16)
        humidity_raw = _extract_bits(value, 40, 8)
        return {
            "battery_level": _decode_battery(battery_raw),
            "battery_raw": battery_raw,
            "temperature": round((temp_raw / 100) + (-40.0), 1),
            "humidity": humidity_raw,
        }

    _LOGGER.debug("Unsupported VMI payload func=%s type=%s", func, device_type)
    return {"raw": payload}
