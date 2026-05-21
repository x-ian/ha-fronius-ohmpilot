"""The Fronius Ohmpilot integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .api import FroniusOhmpilotApiClient
from .const import CONFIG_KEY_HTTP_PORT, CONFIG_KEY_MODBUS_PORT, DEFAULT_HTTP_PORT, DEFAULT_MODBUS_PORT, DOMAIN
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
    coordinator = FroniusOhmpilotDataUpdateCoordinator(hass, api_client, entry.entry_id)

    await coordinator.async_config_entry_first_refresh()

    try:
        device_info = await api_client.async_get_device_info()
        coordinator.serial_number = device_info.get("serial_number", "")
        coordinator.manufacturer = device_info.get("manufacturer", "Fronius") or "Fronius"
        coordinator.model = device_info.get("model", "Ohmpilot") or "Ohmpilot"
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not read device info from Ohmpilot; serial number unavailable: %s", err)

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api_client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    async def update_time(_):
        await api_client.async_set_time()

    unsub = async_track_time_interval(hass, update_time, timedelta(minutes=30))
    entry.async_on_unload(unsub)

    async def update_power(_):
        if not coordinator.active:
            return
        power_entity = hass.data[DOMAIN][entry.entry_id].get("power_number")
        if power_entity is None or power_entity.native_value is None:
            return
        power_limit = int(power_entity.native_value)
        if power_limit > 1:
            await api_client.async_set_power_limit(power_limit)

    unsub2 = async_track_time_interval(hass, update_power, timedelta(seconds=1))
    entry.async_on_unload(unsub2)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
