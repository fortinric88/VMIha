"""Minimal EnOcean serial listener for the VMI Ventilairsec integration.

This module is intentionally lightweight: it opens the configured serial port,
reads raw bytes, and dispatches parsed payloads to the entity layer when possible.
It is designed to work with a USB/serial EnOcean modem on /dev/ttyS2 and to be
compatible with the proprietary VMI payloads from the Jeedom backup.
"""
from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path
from typing import Any, Callable

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover - used when pyserial is not installed
    serial = None  # type: ignore[assignment]

from .enocean_handler import parse_d1079_payload

_LOGGER = logging.getLogger(__name__)


def _guess_device_slug(payload: str) -> str:
    lower = payload.lower()
    if "d1079" in lower or payload.startswith("0x0421574f"):
        return "vmi_purevent"
    if payload.startswith("0x0422407d"):
        return "vmi_assistant_ventilairsec"
    if "a5_09_04" in lower or payload.startswith("0x81003227"):
        return "co2_sensor"
    if "a5_04_01" in lower or payload.startswith("0x810054f5"):
        return "temperature_humidity_sensor"
    return "vmi_purevent"


class EnOceanSerialListener:
    """Background listener reading a serial port for EnOcean telegrams."""

    def __init__(self, port: str = "/dev/ttyS2", callback: Callable[[dict[str, Any]], None] | None = None) -> None:
        self.port = port
        self.callback = callback
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._serial = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        if serial is None:
            _LOGGER.warning("pyserial is not installed; serial listening is disabled")
            return
        _LOGGER.debug("Starting EnOcean listener on port %s", self.port)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        _LOGGER.debug("Stopping EnOcean listener")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:  # pragma: no cover
                pass

    def _run(self) -> None:
        try:
            self._serial = serial.Serial(self.port, 57600, timeout=0.2)
        except Exception as exc:  # pragma: no cover - best effort
            _LOGGER.error("Unable to open EnOcean serial port %s: %s", self.port, exc)
            return

        while not self._stop_event.is_set():
            try:
                if self._serial.in_waiting > 0:
                    data = self._serial.read(self._serial.in_waiting)
                    if data:
                        _LOGGER.debug("Received %d serial bytes", len(data))
                        self._handle_bytes(data)
                else:
                    self._stop_event.wait(0.1)
            except Exception as exc:  # pragma: no cover
                _LOGGER.exception("Error while reading serial data: %s", exc)
                break

    def _handle_bytes(self, data: bytes) -> None:
        text = data.decode("latin-1", errors="ignore")
        if not text:
            return

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        _LOGGER.debug("Decoded %d serial lines", len(lines))
        for line in lines:
            self._process_line(line)

    def _process_line(self, line: str) -> None:
        _LOGGER.debug("Processing EnOcean line: %s", line)
        lower = line.lower()
        if "d1079" in lower or "a5-09-04" in lower or "a5-04-01" in lower:
            payload = line
            self._dispatch_payload(payload)
        else:
            _LOGGER.debug("Ignored EnOcean line, not matching known device patterns: %s", line)

    def _dispatch_payload(self, payload: str) -> None:
        if self.callback is None:
            return
        try:
            token = payload.strip()
            if token.startswith("0x"):
                if token.startswith("0x0422407d"):
                    parsed = parse_d1079_payload(token, func="00", device_type="00")
                    device_slug = "vmi_assistant_ventilairsec"
                else:
                    parsed = parse_d1079_payload(token, func="01", device_type="00")
                    device_slug = _guess_device_slug(token)
                self.callback({"raw": token, "parsed": parsed, "device_slug": device_slug})
                return
            self.callback({"raw": payload, "parsed": {}, "device_slug": _guess_device_slug(payload)})
        except Exception as exc:  # pragma: no cover
            _LOGGER.exception("Unable to parse EnOcean line %s: %s", payload, exc)
        else:
            _LOGGER.debug("Dispatched EnOcean payload %s for %s: %s", token, device_slug, parsed)
