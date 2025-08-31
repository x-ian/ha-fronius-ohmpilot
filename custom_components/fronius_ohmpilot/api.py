"""Fronius Ohmpilot API Client."""

import asyncio
import logging
import time
from typing import Any, Dict

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__package__)


class FroniusOhmpilotApiClient:
    """API client for communicating with the Fronius Ohmpilot."""

    def __init__(
        self, hass: HomeAssistant, host: str, modbus_port: int, http_port: int
    ) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.host = host
        self.modbus_port = modbus_port
        self.http_port = http_port
        self.client = ModbusTcpClient(host, port=modbus_port)
        self.session = async_get_clientsession(hass)

    def _execute_modbus_sync(self, action, *args):
        """Execute a synchronous pymodbus action in an executor."""
        _LOGGER.warning("_execute_modbus_sync")
        try:
            self.client.connect()
            # _LOGGER.warning("_execute_modbus_sync 2: %s | %s", *args, args)
            result = action(*args)
            if result.isError():
                _LOGGER.error("Modbus error: %s", result)
                return None
            _LOGGER.warning("_execute_modbus_sync. No Modbus error: %s", result)
            return result
        except ConnectionException as e:
            _LOGGER.error(
                "Failed to connect to Ohmpilot at %s:%s - %s",
                self.host,
                self.modbus_port,
                e,
            )
            return None
        except Exception as e:
            _LOGGER.error("_execute_modbus_sync exception %s", e)
            return None

        finally:
            _LOGGER.warning("_execute_modbus_sync finally")
            self.client.close()

    async def test_connection(self) -> bool:
        """Test the connection to the Ohmpilot."""
        # Use a simple read to test connection
        result = await self.hass.async_add_executor_job(
            self._execute_modbus_sync, self.client.read_holding_registers, 40799
        )
        _LOGGER.warning("Test_connection: %s", result)
        return result is not None

    async def async_get_data(self) -> Dict[str, Any]:
        """Fetch data from the Ohmpilot via Modbus."""
        data = {}

        def _sync_get_data():
            """Synchronous data fetching logic."""
            self.client.connect()

            # Status
            status_reg = self.client.read_holding_registers(40799, count=1)
            data["status"] = (
                status_reg.registers[0] if not status_reg.isError() else None
            )

            # Temperature
            temp_reg = self.client.read_holding_registers(40808, count=1)
            data["temperature"] = (
                temp_reg.registers[0] / 10 if not temp_reg.isError() else None
            )

            # Power (32-bit)
            power_regs = self.client.read_holding_registers(40800, count=2)
            if not power_regs.isError():
                data["power"] = (power_regs.registers[0] << 16) | power_regs.registers[
                    1
                ]
            else:
                data["power"] = None

            # Energy (64-bit)
            energy_regs = self.client.read_holding_registers(40804, count=4)
            if not energy_regs.isError():
                data["energy"] = (
                    (energy_regs.registers[0] << 48)
                    | (energy_regs.registers[1] << 32)
                    | (energy_regs.registers[2] << 16)
                    | energy_regs.registers[3]
                )
            else:
                data["energy"] = None

            self.client.close()

            _LOGGER.debug("_sync_get_data %s", data)
            return data

        return await self.hass.async_add_executor_job(_sync_get_data)

    async def async_set_power_limit(self, power: int) -> None:
        """Set the power limit via Modbus."""
        # _LOGGER.warning("Set power limit to %s W", power)
        payload = [0, power]
        await self.hass.async_add_executor_job(
            self._execute_modbus_sync, self.client.write_registers, 40599, payload
        )

    async def async_set_target_temperature(self, temp: int) -> None:
        """Set the target temperature via HTTP GET request."""
        # This uses the logic from your rest_command
        url = (
            f"http://{self.host}:{self.http_port}/set.cgi?name=Ohmpilot&H1Auto=manually&H1Ph=3+phasig"
            f"&H1Power=3709&tempInst=on&legCyc=0&maxTempUsed=on&maxTempCyc={temp}"
            f"&H2Ph=aus&H2Power=0&H2ThModeOn=Einspeisung&H2ThOn=4000"
            f"&H2ThModeOff=Einspeisung&H2ThOff=0"
        )
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            # _LOGGER.warning("Set target temperature to %s °C", temp)
            # _LOGGER.warning("Set target temperature to %s °C", url)
        except Exception as e:
            _LOGGER.error("Failed to set target temperature: %s", e)

    async def async_set_time(self) -> None:
        """Set the system time on the Ohmpilot via Modbus."""
        # _LOGGER.warning("Ohmpilot system time synchronized.")
        now = int(time.time())
        high_word = (now >> 16) & 0xFFFF
        low_word = now & 0xFFFF
        # Assuming timezone +2h = 120 minutes (standard for Germany in summer)
        now_struct = time.localtime()
        if now_struct.tm_isdst > 0 and time.daylight:
            timezone_offset_minutes = -time.altzone // 60
        else:
            timezone_offset_minutes = -time.timezone // 60

        # TODO: Make timezone configurable or dynamic
        payload = [0, 0, high_word, low_word, 120]

        await self.hass.async_add_executor_job(
            self._execute_modbus_sync, self.client.write_registers, 40399, payload
        )
