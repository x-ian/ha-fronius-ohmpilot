"""DataUpdateCoordinator for the Fronius Ohmpilot."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FroniusOhmpilotApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__package__)


class FroniusOhmpilotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Fronius Ohmpilot."""

    def __init__(self, hass: HomeAssistant, api_client: FroniusOhmpilotApiClient):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=False,
        )
        self.api = api_client

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await self.api.async_get_data()
            if data is None or not any(v is not None for v in data.values()):
                raise UpdateFailed("No data received from Ohmpilot")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
