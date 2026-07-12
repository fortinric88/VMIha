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
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
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

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            self._process_line(line)

    def _process_line(self, line: str) -> None:
        lower = line.lower()
        if "d1079" in lower or "a5-09-04" in lower or "a5-04-01" in lower:
            payload = line
            self._dispatch_payload(payload)

    def _dispatch_payload(self, payload: str) -> None:
        if self.callback is None:
            return
        try:
            # Best-effort parse: if a token resembles a VMI payload, hand it to the parser.
            parts = payload.split()
            for part in parts:
                if part.startswith("0x") and len(part) >= 10:
                    self.callback({"raw": part, "parsed": parse_d1079_payload(part, func="01", device_type="00")})
                    return
            self.callback({"raw": payload, "parsed": {}})
        except Exception as exc:  # pragma: no cover
            _LOGGER.exception("Unable to parse EnOcean line %s: %s", payload, exc)
