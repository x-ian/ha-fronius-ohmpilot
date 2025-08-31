"""The Fronius Ohmpilot integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .api import FroniusOhmpilotApiClient
from .const import DOMAIN
from .coordinator import FroniusOhmpilotDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


_PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type FroniusConfigEntry = ConfigEntry[MyApi]  # noqa: F821


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Ohmpilot from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.warning("async_setup_entry %s ", entry.data[CONF_HOST])
    _LOGGER.warning("async_setup_entry %s ", entry.data)
    host = entry.data[CONF_HOST]
    modbus_port = 503  # entry.data['modbus_port']
    http_port = 81  # entry.data['http_port']

    api_client = FroniusOhmpilotApiClient(hass, host, modbus_port, http_port)
    coordinator = FroniusOhmpilotDataUpdateCoordinator(hass, api_client)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api_client,
        "coordinator": coordinator,
    }
    entry.runtime_data = api_client

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    # Register the service to set time
    # async def set_time_service(call: ServiceCall):
    #     """Service call to set the Ohmpilot time."""
    #     await api_client.async_set_time()

    # setting the time on ohmpilot
    # hass.services.async_register(DOMAIN, "sync_time", set_time_service)

    # Define the function to be called by the timer
    # async def sync_time_interval(now=None):
    #     _LOGGER.warning("Executing periodic Ohmpilot time sync.")
    #     await api_client.async_set_time()
    # # Automatically sync time every hour, like in the AppDaemon script
    # # async_track_time_interval(hass, lambda now: api_client.async_set_time(), timedelta(hours=1))
    # # async_track_time_interval(hass, lambda now: api_client.async_set_time(), timedelta(minutes=1))
    # # Set up the interval to run every minute and capture the remover function
    # remover = async_track_time_interval(hass, sync_time_interval, timedelta(minutes=60))
    # # Register a listener to call the remover function when the integration is unloaded
    # entry.async_on_unload(remover)

    # # Every 10 secs set the Power (as otherwise the Ohmpilot goes into failure mode)
    # # Define the function to be called by the timer
    # async def sync_power_interval(now=None):
    #     _LOGGER.warning("Executing periodic Ohmpilot power sync.")
    #     await api_client.async_set_power_limit(500)
    # # async_track_time_interval(hass, lambda now: api_client.async_set_power_limit(500), timedelta(seconds=3))
    # remover_power = async_track_time_interval(hass, sync_power_interval, timedelta(seconds=1))
    # # Register a listener to call the remover function when the integration is unloaded
    # entry.async_on_unload(remover_power)

    return True


# # TODO Update entry annotation
# async def async_setup_entry(hass: HomeAssistant, entry: FroniusConfigEntry = ConfigEntry[MyApi]  # noqa: F821
# ) -> bool:
#     """Set up Fronius Ohmpilot from a config entry."""

# async def async_setup_entry(hass: HomeAssistant, entry: FroniusConfigEntry) -> bool:
#     """Set up fronius from a config entry."""
#     session = async_get_clientsession(hass)
#     api = FroniusOhmpilotApiClient(entry.data[CONF_HOST], session)

#     entry.runtime_data = api

#     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

#     return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
