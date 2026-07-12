"""Config flow for VMI Ventilairsec."""
from __future__ import annotations

try:
    import voluptuous as vol
except Exception:  # pragma: no cover - protect import-time in environments without voluptuous
    vol = None  # type: ignore

from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the integration using the standard handler name."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VmiVentilairsecOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="VMI Ventilairsec", data={"serial_port": user_input["serial_port"]})

        if vol is None:
            # voluptuous missing — show an empty form (user can edit options later)
            return self.async_show_form(step_id="user")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("serial_port", default="/dev/ttyS2"): str,
            }),
        )


class VmiVentilairsecOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        if vol is None:
            return self.async_show_form(step_id="init")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("serial_port", default=self.config_entry.options.get("serial_port", "/dev/ttyS2")): str,
            }),
        )
