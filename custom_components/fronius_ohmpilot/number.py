"""Number platform for Fronius Ohmpilot."""

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONFIG_KEY_HEATER1_MAX_POWER, DEFAULT_HEATER1_MAX_POWER, DOMAIN
from .coordinator import FroniusOhmpilotDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: FroniusOhmpilotDataUpdateCoordinator = data["coordinator"]

    power_entity = OhmpilotMaxPowerNumber(coordinator, entry)
    hass.data[DOMAIN][entry.entry_id]["power_number"] = power_entity

    async_add_entities([power_entity, OhmpilotMaxTempNumber(coordinator, entry)])


class OhmpilotBaseNumber(RestoreNumber):
    """Base class for Ohmpilot number entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry):
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_device_info = coordinator.device_info
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        """Restore last known value on startup."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_number_data()) is not None:
            self._attr_native_value = last_data.native_value


class OhmpilotMaxPowerNumber(OhmpilotBaseNumber):
    """Representation of the Maximum Power setting."""

    _attr_name = "Output Power"
    _attr_icon = "mdi:lightning-bolt"
    _attr_native_unit_of_measurement = "W"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_step = 100

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize with configurable max power."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_output_power"
        self._attr_native_max_value = float(entry.data.get(CONFIG_KEY_HEATER1_MAX_POWER, DEFAULT_HEATER1_MAX_POWER))

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._coordinator.api.async_set_power_limit(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()


class OhmpilotMaxTempNumber(OhmpilotBaseNumber):
    """Representation of the Maximum Temperature setting."""

    _attr_name = "Target Temperature"
    _attr_icon = "mdi:coolant-temperature"
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 10
    _attr_native_max_value = 55
    _attr_native_step = 5

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_target_temperature"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._coordinator.api.async_set_target_temperature(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()
