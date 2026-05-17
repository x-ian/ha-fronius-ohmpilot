"""Constants for the Fronius Ohmpilot integration."""

DOMAIN = "fronius_ohmpilot"

CONFIG_KEY_MODBUS_PORT = "modbus_port"
CONFIG_KEY_HTTP_PORT = "http_port"
CONFIG_KEY_HEATER1_MAX_POWER = "heater1_maximum_power"

DEFAULT_MODBUS_PORT = 503
DEFAULT_HTTP_PORT = 81
DEFAULT_HEATER1_MAX_POWER = 3700

OUTPUT_POWER_ENTITY_ID = "number.fronius_ohmpilot_output_power"
