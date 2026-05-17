"""Switch platform for Fronius Ohmpilot."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, OUTPUT_POWER_ENTITY_ID
from .coordinator import FroniusOhmpilotDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        OhmpilotIntegrationActiveSwitch(coordinator, entry),
    ]
    async_add_entities(entities)


class OhmpilotIntegrationActiveSwitch(SwitchEntity, RestoreEntity):
    """Switch that pauses/resumes Ohmpilot polling and power limit writes."""

    def __init__(
        self,
        coordinator: FroniusOhmpilotDataUpdateCoordinator,
        entry: ConfigEntry,
    ):
        """Initialize the switch."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_is_on = True
        self._attr_name = "Fronius Ohmpilot Integration Active"
        self._attr_unique_id = "882c46a0-550a-42ba-afa5-e0b86d3ae979"
        self._attr_icon = "mdi:power-plug"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Fronius Ohmpilot",
            manufacturer="Fronius",
            model="Ohmpilot",
        )

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
        if (state := self.hass.states.get(OUTPUT_POWER_ENTITY_ID)) is not None and state.state not in (
            "unavailable",
            "unknown",
            "none",
        ):
            try:
                power_limit = int(float(state.state))
                if power_limit > 1:
                    await self._coordinator.api.async_set_power_limit(power_limit)
            except (ValueError, TypeError):
                pass
        await self._coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Stop the device and pause polling and power limit writes."""
        await self._coordinator.api.async_set_power_limit(0)
        self._coordinator.active = False
        self._attr_is_on = False
        self.async_write_ha_state()
