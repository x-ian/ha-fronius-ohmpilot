"""Switch platform for Fronius Ohmpilot."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""

    entities = [
        OhmpilotIntegrationActiveSwitch(entry),
    ]
    async_add_entities(entities)


class OhmpilotIntegrationActiveSwitch(SwitchEntity):
    """Representation of the Integration Active switch."""

    def __init__(self, entry: ConfigEntry):
        """Initialize the switch."""
        self._entry = entry
        self._attr_is_on = True  # Default to on when Home Assistant starts
        self._attr_name = "Fronius Ohmpilot Integration Active"
        self._attr_unique_id = "882c46a0-550a-42ba-afa5-e0b86d3ae979"
        self._attr_icon = "mdi:power-plug"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Fronius Ohmpilot",
            manufacturer="Fronius",
            model="Ohmpilot",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()
