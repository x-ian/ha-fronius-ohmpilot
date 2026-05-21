"""Sensor platform for Fronius Ohmpilot."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FroniusOhmpilotDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: FroniusOhmpilotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            OhmpilotTemperatureSensor(coordinator, entry),
            OhmpilotPowerSensor(coordinator, entry),
            OhmpilotEnergySensor(coordinator, entry),
            OhmpilotStatusSensor(coordinator, entry),
        ]
    )


class OhmpilotBaseSensor(CoordinatorEntity[FroniusOhmpilotDataUpdateCoordinator], SensorEntity):
    """Base class for Ohmpilot sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = coordinator.device_info


class OhmpilotTemperatureSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Temperature sensor."""

    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_temperature"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("temperature")


class OhmpilotPowerSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Power sensor."""

    _attr_name = "Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_power"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("power")


class OhmpilotEnergySensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Energy sensor."""

    _attr_name = "Energy Consumed"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "Wh"
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_energy_consumed"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("energy")


class OhmpilotStatusSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Status Code sensor."""

    _attr_name = "State Code"
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator, entry)
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_state_code"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("status")
