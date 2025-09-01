# Home Assistant Integration für Fronius Ohmpilot

* Gen24 can be configured to push all its excess PV power into the Ohmpilot up to a configurable temperature. It is not possible to reduce the maximum output; all the excess power is always used for the Ohmpilot (up to the maximum power of the heating rod). For peak shaving or reducing risk of calcification this isn't ideal. Especially with PV forecast it should be possible to ensure a certain end temperature at a specific point by spreading out the heating process of a longer period (and with lower power power). But the combination of Gen24 and Ohmpilot doesn't support this.
* Wifi of Ohmpilot seems unreliable. Stops every few days and needs power-cycle
* Ohmpilot uses ModbusRS484 (via dedicated wiring) and as fallback ModbusTCP
* ModbusTCP scans local subnet and connects to Gen24 automatically
* Ohmpilot receives constants updates from Gen24
* If no messages from Gen24 arrived, it stops operation (current power message expected at minimum every 30 secs (maybe this needs to be even more frequent?), timestamp every 6 hours)
* To prevent this IP auto-conenction, Ohmpilot needs to be in another subnet
* This can be a simple router/gateway/access point placing the Ohmpilot in its own subnet
* This router/gateway/accesspoint then needs a port forward to make the modbus port of the Ohmpilot (503) accessible from the outside subnet
* Once this is done, the Ohmpilot can be remotely configured on the fly by Homeassistant or other systems through HTTP calls to its local web interface
* Remember: This only works if the RS484 modbus wires are disconnected and the IP auto-discovery from the Gen24 fails

Useful links: 

* https://github.com/mstroh76/cohmpilot/blob/main/cohmpilot.c
* https://www.photovoltaikforum.com/thread/228127-ohmpilot-modbus-tcp-register-map/?pageNo=3
* https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/456735-fronius-ohmpilot-heizstab-modbus-tcp-hex-wert-senden
* https://github.com/roelof4/Ohmpilot
* https://smartfox.at/wp-content/uploads/2022/12/Anleitung-Einbindung-Ansteuerung-Fronius-Ohmpilot.pdf

### Todo

1. Document default Ohmpilot behavious
1. Draw network topology
1. make power range of specific Ohmpilot configurable (or even fetch from HTTP admin)
1. Values for current power setting and target temp aren't persisted during reboots
1. Properly utilize timezone
1. Make port-forwards for modbus and http fully configurable

### Dev env setup

1. Setup default HomeAssistant dev environment
1. Clone this repo somewhere on your local machine
1. Mount the repo into your devcontainter (in devcontainer.json)
```
  // hack to somehow make my custom component accessible in the outside
  "mounts": [
    "source=/Users/xian/projects/solar-playground/ha-fronius-ohmpilot/custom_components/fronius_ohmpilot,target=/workspaces/home-assistant-core/config/custom_components/fronius_ohmpilot,type=bind,consistency=cached"
  ],
```