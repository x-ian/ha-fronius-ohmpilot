"""Sensor platform for Fronius Ohmpilot."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
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
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        OhmpilotTemperatureSensor(coordinator, entry),
        OhmpilotPowerSensor(coordinator, entry),
        OhmpilotEnergySensor(coordinator, entry),
        OhmpilotStatusSensor(coordinator, entry),
    ]
    async_add_entities(entities)


class OhmpilotBaseSensor(
    CoordinatorEntity[FroniusOhmpilotDataUpdateCoordinator], SensorEntity
):
    """Base class for Ohmpilot sensors."""

    def __init__(
        self, coordinator: FroniusOhmpilotDataUpdateCoordinator, entry: ConfigEntry
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Fronius Ohmpilot",
            manufacturer="Fronius",
            model="Ohmpilot",
        )


class OhmpilotTemperatureSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Temperature sensor."""

    _attr_name = "Fronius Ohmpilot Integration Temperature"
    _attr_unique_id = "33bce9d7-958a-4999-9ff5-a944d180aefc"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"
    _attr_icon = "mdi:thermometer"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("temperature")


class OhmpilotPowerSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Power sensor."""

    _attr_name = "Fronius Ohmpilot Integration Power"
    _attr_unique_id = "588daa8b-f42c-4082-8371-d1c243054728"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_icon = "mdi:flash"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("power")


class OhmpilotEnergySensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Energy sensor."""

    _attr_name = "Fronius Ohmpilot Integration Energy Consumed"
    _attr_unique_id = "54f07913-1686-4a58-a414-b585feb0b4cb"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "Wh"
    _attr_icon = "mdi:flash"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("energy")


class OhmpilotStatusSensor(OhmpilotBaseSensor):
    """Representation of the Ohmpilot Status Code sensor."""

    _attr_name = "Fronius Ohmpilot Integration State Code"
    _attr_unique_id = "c9a33e12-db67-43be-9ebc-9d6f95e81196"
    _attr_icon = "mdi:information-outline"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("status")
