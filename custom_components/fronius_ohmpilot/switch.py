"""Switch platform for Fronius Ohmpilot."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .coordinator import FroniusOhmpilotDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: FroniusOhmpilotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([OhmpilotActiveSwitch(coordinator, entry)])


class OhmpilotActiveSwitch(SwitchEntity, RestoreEntity):
    """Switch that pauses/resumes Ohmpilot polling and power limit writes."""

    _attr_has_entity_name = True
    _attr_name = "Active"
    _attr_icon = "mdi:power-plug"

    def __init__(
        self,
        coordinator: FroniusOhmpilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ):
        """Initialize the switch."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_is_on = True
        serial = coordinator.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_active"
        self._attr_device_info = coordinator.device_info

    async def async_added_to_hass(self) -> None:
        """Restore last known state on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == STATE_ON
            self._coordinator.active = self._attr_is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Resume polling and power limit writes."""
        self._coordinator.active = True
        self._attr_is_on = True
        power_entity = self.hass.data[DOMAIN][self._entry.entry_id].get("power_number")
        if power_entity is not None and power_entity.native_value is not None:
            power_limit = int(power_entity.native_value)
            if power_limit > 1:
                await self._coordinator.api.async_set_power_limit(power_limit)
        await self._coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Stop the device and pause polling and power limit writes."""
        await self._coordinator.api.async_set_power_limit(0)
        self._coordinator.active = False
        self._attr_is_on = False
        self.async_write_ha_state()
