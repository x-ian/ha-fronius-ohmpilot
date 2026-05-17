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

### Via HACS (Recommended) - NOT YET

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
   - **Maximum Power of Heater 1** — default `3700`

The integration tests the Modbus connection before saving.

## Usage

### Power Limit

The **Maximum Power** number entity controls how much power (in watts) the Ohmpilot is allowed to consume. The integration writes this value to the device every second via Modbus. Set it to `0` to stop diversion without turning off the device.

### Target Temperature

The **Maximum Temperature** number entity sends an HTTP request to the Ohmpilot's `/set.cgi` endpoint to set the boiler cutoff temperature (10–55 °C in 5 °C steps).

### Integration Active Switch

Turning this switch **off** suspends all Modbus polling and power limit writes immediately. Turning it back **on** resumes polling and triggers an immediate data refresh. Use this to pause the integration without removing it (e.g. during maintenance or when the device is offline).

## Common and Installation notes

* Gen24 can be configured to push all its excess PV power into the Ohmpilot up to a configurable temperature. It is not possible to reduce the maximum output; all the excess power is always used for the Ohmpilot (up to the maximum power of the heating rod). For peak shaving or reducing risk of calcification this isn't ideal. Especially with PV forecast it should be possible to ensure a certain end temperature at a specific point by spreading out the heating process over a longer period (and with lower power power). But the combination of Gen24 and Ohmpilot doesn't support this.
* Wifi of Ohmpilot seems unreliable. Stops every few days and needs power-cycle
* Ohmpilot uses ModbusRS484 (via dedicated wiring) and as fallback ModbusTCP
* Ohmpilot receives constants updates from Gen24
* If no messages from Gen24 arrived, it stops operation
  * 'current power' message expected at minimum every 30 secs (maybe even more frequent?)
  * timestamp message every 6 hours)

* ModbusTCP scans local subnet and connects to Gen24 automatically
* To prevent the IP auto-discovery and connectivity, Ohmpilot needs to be in another subnet
* This can be a simple router/gateway/access point placing the Ohmpilot in its own subnet
* This router/gateway/accesspoint then needs a port forward to make the modbus port of the Ohmpilot (503) accessible from the outside subnet
* Once this is done, the Ohmpilot can be remotely configured on the fly by Homeassistant or other systems through HTTP calls to its local web interface
* Remember: This only works if the RS484 modbus wires are disconnected and the IP auto-discovery from the Gen24 fails

* Appears as if Online firmware updates aren't working - even for Gen24 updates only appeared in solarweb after Ohmpilot was connected again to Gen24. Temporarily switching Ethernet connection back to main router (instead of router just for the Ohmpilot) (and potentially a restart of Ohmpilot) solved the problem

Known firmware versions:

* OhmPilot 1.0.26 & Gen24 1.36.6-1
* OhmPilot: 1.0.29-1 & Gen 24 1.40.8-1

Useful links:

* https://github.com/mstroh76/cohmpilot/blob/main/cohmpilot.c
* https://www.photovoltaikforum.com/thread/228127-ohmpilot-modbus-tcp-register-map/?pageNo=3
* https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/456735-fronius-ohmpilot-heizstab-modbus-tcp-hex-wert-senden
* https://github.com/roelof4/Ohmpilot
* https://smartfox.at/wp-content/uploads/2022/12/Anleitung-Einbindung-Ansteuerung-Fronius-Ohmpilot.pdf

### Todo

1. Draw network topology
1. make power range of specific Ohmpilot configurable (or even fetch from HTTP admin)
1. Values for current power setting and target temp aren't persisted during reboots
1. Properly utilize timezone
1. Make port-forwards for modbus and http fully configurable
1. Dont use hardcoded UUIDs; maybe each Ohmpilot has its own ID (or mac address) and use these for HA IDs
1. Document known version for Gen24 and Ohmpilot
1. Support heater 2
1. Support multiple Ohmpilots

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
