from pymodbus.client import ModbusTcpClient
import logging
import time

def setPower(power):
    client = ModbusTcpClient('192.168.1.5', port=503)  # Replace with your Ohmpilot IP
    # client = ModbusTcpClient('192.168.1.44')  # Replace with your Ohmpilot IP
    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    client.connect()

    # Set power limit to 1000W (example)
    client.write_registers(40599, power)

    client.close()

def getStatus():
    client = ModbusTcpClient('192.168.1.5', port=503)  # Replace with your Ohmpilot IP
    # client = ModbusTcpClient('192.168.1.44')  # Replace with your Ohmpilot IP
    # logging.basicConfig()
    # log = logging.getLogger()
    # log.setLevel(logging.DEBUG)

    client.connect()

    status = client.read_holding_registers(40799).registers
    temp = client.read_holding_registers(40808).registers
    
    # Read 32-bit power value from two consecutive 16-bit registers
    power_regs = client.read_holding_registers(40800, count=2).registers
    power = (power_regs[0] << 16) | power_regs[1]
    # Read 64-bit energy value from two consecutive 32-bit registers (4 registers total, 16 bits each)
    energy_regs = client.read_holding_registers(40804, count=4).registers
    # Combine the 4 registers into a 64-bit integer (big-endian)
    energy = (energy_regs[0] << 48) | (energy_regs[1] << 32) | (energy_regs[2] << 16) | energy_regs[3]

    print(f"Status: {status}")
    print(f"Power: {power} W")
    print(f"Energy: {energy} Wh")
    print(f"Temperature: {temp} deg C")
    client.close()

def setTime():
    # Aktuelle Zeit als Unix-Timestamp in Sekunden
    now = int(time.time())

    # High- und Low-Word (16 Bit) aus 32-Bit Timestamp
    high_word = (now >> 16) & 0xFFFF
    low_word = now & 0xFFFF

    # msg.payload als Array mit 5 Registern (erst 2 Register = 0, dann Zeit, dann 120 [Zeitzone +2h = 120])
    payload = [0, 0, high_word, low_word, 120]
    
    client = ModbusTcpClient('192.168.1.5', port=503)
    client.connect()
    client.write_registers(40399, values=payload) 

    client.close()

# time needs to be set every 6 hours
setTime()

# power needs to be set every 30 seconds
setPower([0, 500])

getStatus()