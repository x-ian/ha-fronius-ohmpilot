# Fronius Ohmpilot — Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A Home Assistant custom integration for the **Fronius Ohmpilot** — a smart solar surplus energy diverter that routes excess PV power to a resistive load (typically a hot water boiler) instead of feeding it back to the grid.

## What is the Fronius Ohmpilot?

The Ohmpilot is a device by [Fronius](https://www.fronius.com/) that continuously regulates power flow to a resistive heater element. It monitors surplus solar generation and throttles the heater between 0 W and its maximum rated load so that grid feed-in stays near zero. This turns unused PV energy into hot water rather than wasting it.

This integration connects Home Assistant to the Ohmpilot using:

- **Modbus TCP** — reads live data (power, energy, temperature, status) and writes the power limit and system time
- **HTTP** — sets the target maximum water temperature via the device's built-in web interface

## Features

- Live sensor readings updated every 5 seconds
- Adjustable power limit and target temperature from the HA UI
- Automatic system time synchronisation every 30 minutes
- Enable/disable switch to pause all communication without removing the integration

## Platforms

| Platform | Entity | Description |
| --- | --- | --- |
| `sensor` | Temperature | Internal temperature of the Ohmpilot (°C) |
| `sensor` | Power | Current power being diverted (W) |
| `sensor` | Energy Consumed | Cumulative energy diverted (Wh) |
| `sensor` | State Code | Raw Modbus status register value |
| `number` | Maximum Power | Power limit sent to the device (0–3700 W) |
| `number` | Maximum Temperature | Target water temperature cutoff (10–55 °C) |
| `switch` | Integration Active | Pause/resume polling and power limit writes |

## Installation

### Via HACS (Recommended)

1. In HACS → Integrations → three-dot menu → **Custom repositories**
2. Add this repository URL and set category to **Integration**
3. Find **Fronius Ohmpilot** and click **Download**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/fronius_ohmpilot/` into your HA `custom_components/` directory
2. Restart Home Assistant

## Configuration

1. **Settings → Devices & Services → + Add Integration → Fronius Ohmpilot**
2. Enter:
   - **Host** — IP address of the Ohmpilot
   - **Modbus Port** — default `503`
   - **HTTP Port** — default `81`

The integration tests the Modbus connection before saving.

## Usage

### Power Limit

The **Maximum Power** number entity controls how much power (in watts) the Ohmpilot is allowed to consume. The integration writes this value to the device every second via Modbus. Set it to `0` to stop diversion without turning off the device.

### Target Temperature

The **Maximum Temperature** number entity sends an HTTP request to the Ohmpilot's `/set.cgi` endpoint to set the boiler cutoff temperature (10–55 °C in 5 °C steps).

### Integration Active Switch

Turning this switch **off** suspends all Modbus polling and power limit writes immediately. Turning it back **on** resumes polling and triggers an immediate data refresh. Use this to pause the integration without removing it (e.g. during maintenance or when the device is offline).

## Troubleshooting

### Connection fails at setup

- Verify the Ohmpilot's IP address is reachable from the HA host
- Confirm Modbus TCP is enabled on the device (port 503 by default)
- Check that no firewall blocks the Modbus port

### Entities show "Unavailable"

- Check that the Ohmpilot is powered on and reachable
- Enable debug logging and inspect `config/home-assistant.log`:

```yaml
logger:
  default: warning
  logs:
    custom_components.fronius_ohmpilot: debug
```

## Development

```bash
# Start local Home Assistant for testing
./script/develop

# Validate (type-check + lint + spell)
script/check

# Run tests
script/test
```

See [AGENTS.md](AGENTS.md) for full developer and AI-agent guidance.

---

[releases-shield]: https://img.shields.io/github/release/x-ian/fronius_ohmpilot.svg?style=for-the-badge
[releases]: https://github.com/x-ian/fronius_ohmpilot/releases
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/x-ian/fronius_ohmpilot.svg?style=for-the-badge
