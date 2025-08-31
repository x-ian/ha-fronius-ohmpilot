"""Number platform for Fronius Ohmpilot."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import FroniusOhmpilotApiClient
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    api_client = data["api"]

    entities = [
        OhmpilotMaxPowerNumber(api_client, entry),
        OhmpilotMaxTempNumber(api_client, entry),
    ]
    async_add_entities(entities)


class OhmpilotBaseNumber(NumberEntity):
    """Base class for Ohmpilot number entities."""

    def __init__(self, api_client: FroniusOhmpilotApiClient, entry: ConfigEntry):
        """Initialize the number entity."""
        self.api = api_client
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Fronius Ohmpilot",
            manufacturer="Fronius",
            model="Ohmpilot",
        )
        # We don't read these values back, so we set a default state
        self._attr_native_value = None


class OhmpilotMaxPowerNumber(OhmpilotBaseNumber):
    """Representation of the Maximum Power setting."""

    _attr_name = "Fronius Ohmpilot Integration Maximum Power"
    _attr_unique_id = "5f5b5c73-a353-4069-b9d4-bf124f39e555"
    _attr_icon = "mdi:lightning-bolt"
    _attr_native_unit_of_measurement = "W"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 3700  # Based on your YAML
    _attr_native_step = 100

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.api.async_set_power_limit(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()


class OhmpilotMaxTempNumber(OhmpilotBaseNumber):
    """Representation of the Maximum Temperature setting."""

    _attr_name = "Fronius Ohmpilot Integration Maximum Temperature"
    _attr_unique_id = "f411747b-5b41-4d31-b38f-728b2cd1c27b"
    _attr_icon = "mdi:coolant-temperature"
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 10  # Based on your YAML
    _attr_native_max_value = 55
    _attr_native_step = 5

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.api.async_set_target_temperature(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()


class OhmpilotActive(OhmpilotBaseNumber):
    """Representation of the Active setting."""

    _attr_name = "Fronius Ohmpilot Integration Active"
    _attr_unique_id = "882c46a0-550a-42ba-afa5-e0b86d3ae979"
    _attr_icon = "mdi:toggle"
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 10  # Based on your YAML
    _attr_native_max_value = 55
    _attr_native_step = 5

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.api.async_set_target_temperature(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()
