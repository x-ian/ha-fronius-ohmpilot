"""The Fronius Ohmpilot integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .api import FroniusOhmpilotApiClient
from .const import (
    CONFIG_KEY_HTTP_PORT,
    CONFIG_KEY_MODBUS_PORT,
    DEFAULT_HTTP_PORT,
    DEFAULT_MODBUS_PORT,
    DOMAIN,
    OUTPUT_POWER_ENTITY_ID,
)
from .coordinator import FroniusOhmpilotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Ohmpilot from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    modbus_port = entry.data.get(CONFIG_KEY_MODBUS_PORT, DEFAULT_MODBUS_PORT)
    http_port = entry.data.get(CONFIG_KEY_HTTP_PORT, DEFAULT_HTTP_PORT)

    api_client = FroniusOhmpilotApiClient(hass, host, modbus_port, http_port)
    coordinator = FroniusOhmpilotDataUpdateCoordinator(hass, api_client)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api_client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    async def update_time(_now):
        await api_client.async_set_time()

    unsub = async_track_time_interval(hass, update_time, timedelta(minutes=30))
    entry.async_on_unload(unsub)

    async def update_power(_now):
        if not coordinator.active:
            return
        if (state := hass.states.get(OUTPUT_POWER_ENTITY_ID)) is None or state.state in (
            "unavailable",
            "unknown",
        ):
            return
        try:
            power_limit = int(float(state.state))
        except ValueError:
            _LOGGER.warning("Could not parse power limit from %s", OUTPUT_POWER_ENTITY_ID)
            return
        if power_limit > 1:
            await api_client.async_set_power_limit(power_limit)

    unsub2 = async_track_time_interval(hass, update_power, timedelta(seconds=1))
    entry.async_on_unload(unsub2)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
