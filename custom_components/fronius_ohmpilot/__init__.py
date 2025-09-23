"""The Fronius Ohmpilot integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
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

    host = entry.data[CONF_HOST]
    modbus_port = 503  # TODO entry.data['modbus_port']
    http_port = 81  # TODO entry.data['http_port']

    api_client = FroniusOhmpilotApiClient(hass, host, modbus_port, http_port)
    coordinator = FroniusOhmpilotDataUpdateCoordinator(hass, api_client)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api_client,
        "coordinator": coordinator,
    }
    entry.runtime_data = api_client

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    # set time on ohmpilot every 30 mins
    async def update_time(now):
        await api_client.async_set_time()

    unsub = async_track_time_interval(
        hass,
        update_time,
        timedelta(minutes=30),
    )
    entry.async_on_unload(unsub)

    # set power limit on ohmpilot every 10 secs
    async def update_power(now):
        # TODO: Make this configurable
        # TODO: Replace with your actual entity ID
        power_limit_entity_id = "number.fronius_ohmpilot_integration_maximum_power"
        if (state := hass.states.get(power_limit_entity_id)) is None or state.state in (
            "unavailable",
            "unknown",
        ):
            return

        try:
            power_limit = int(float(state.state))
        except ValueError:
            _LOGGER.warning(
                "Could not parse power limit from %s", power_limit_entity_id
            )
            return
        if power_limit > 1:
            await api_client.async_set_power_limit(power_limit)

    unsub2 = async_track_time_interval(
        hass,
        update_power,
        timedelta(seconds=1),
    )
    entry.async_on_unload(unsub2)

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


# async def async_setup_time_sync(hass: HomeAssistant, entry: BalboaConfigEntry) -> None:
#     """Set up the time sync."""

#     _LOGGER.debug("Setting up 30-mins time sync")
#     api_client = entry.runtime_data
#     await api_client.async_set_time()

#     async def sync_time(now: datetime) -> None:
#         now = dt_util.as_local(now)
#         if (now.hour, now.minute) != (spa.time_hour, spa.time_minute):
#             _LOGGER.debug("Syncing time with Home Assistant")
#             await spa.set_time(now.hour, now.minute)

#     await sync_time(dt_util.utcnow())
#     entry.async_on_unload(
#         async_track_time_interval(hass, sync_time, SYNC_TIME_INTERVAL)
#     )
