"""DataUpdateCoordinator for the Fronius Ohmpilot."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FroniusOhmpilotApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__package__)


class FroniusOhmpilotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Fronius Ohmpilot."""

    def __init__(self, hass: HomeAssistant, api_client: FroniusOhmpilotApiClient, entry_id: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            always_update=False,
        )
        self.api = api_client
        self.entry_id = entry_id
        self.active: bool = True
        self.serial_number: str = ""
        self.manufacturer: str = "Fronius"
        self.model: str = "Ohmpilot"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info using the serial number as the stable identifier."""
        identifier = self.serial_number or self.entry_id
        name = f"Fronius Ohmpilot {self.serial_number}" if self.serial_number else "Fronius Ohmpilot"
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=name,
            manufacturer=self.manufacturer or "Fronius",
            model=self.model or "Ohmpilot",
            serial_number=self.serial_number or None,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        if not self.active:
            return self.data
        try:
            data = await self.api.async_get_data()
            if data is None or not any(v is not None for v in data.values()):
                raise UpdateFailed("No data received from Ohmpilot")  # noqa: TRY301
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        else:
            return data
