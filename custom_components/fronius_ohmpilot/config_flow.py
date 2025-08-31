"""Config flow for the Fronius Ohmpilot integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import FroniusOhmpilotApiClient
from .const import (
    CONFIG_KEY_HTTP_PORT,
    CONFIG_KEY_MODBUS_PORT,
    DEFAULT_HTTP_PORT,
    DEFAULT_MODBUS_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="192.168.1.5"): str,
        vol.Required(CONFIG_KEY_MODBUS_PORT, default=DEFAULT_MODBUS_PORT): int,
        vol.Required(CONFIG_KEY_HTTP_PORT, default=DEFAULT_HTTP_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    client = FroniusOhmpilotApiClient(
        hass=hass,
        host=data["host"],
        modbus_port=data["modbus_port"],
        http_port=data["http_port"],
    )
    if not await client.test_connection():
        _LOGGER.error("validate_input ConnectionError")
        raise CannotConnect
    return {"title": f"Fronius Ohmpilot ({data['host']})"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fronius Ohmpilot."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigFlow.ConfigEntry,
    ) -> ConfigFlow.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Fronius Ohmpilot."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the new connection details
                await validate_input(self.hass, user_input)

                # Update the config entry with the new data
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
                # Reload the integration to apply the new settings
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                # Close the options flow
                return self.async_create_entry(title="", data={})

            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        # Pre-populate the form with the current settings
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=self.config_entry.data.get(CONF_HOST)
                ): str,
                vol.Required(
                    "modbus_port",
                    default=self.config_entry.data.get(
                        CONFIG_KEY_MODBUS_PORT, DEFAULT_MODBUS_PORT
                    ),
                ): int,
                vol.Required(
                    "http_port",
                    default=self.config_entry.data.get(
                        CONFIG_KEY_HTTP_PORT, DEFAULT_HTTP_PORT
                    ),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
