# Ohmpilot controller migrated from C to Python
# Dependencies: pymodbus, requests

import time
import signal
import struct
import datetime
import requests
import os
from pymodbus.client import ModbusTcpClient

# Constants
MB_SERVER = "192.168.1.44"
# SMART_METER_IP = "192.168.0.11"
# USER = "4E2609D53341"
# PASS = "18321456"
CSV_PATH = os.path.expanduser("./")

# Temperature calibration
TEMP_K = 1.03
TEMP_D = 3.80

# Power settings
MAX_TEMP = 52.5
TIME_INTERVAL_HOURS = 6
MIN_HEATER_POWER = 275
RESERVED_POWER = 105
MIN_SET_POWER_CHANGE = 15
SLEEP_SECONDS = 20

# Modbus register addresses
ADD_MANUF = 40004
ADD_DEVICE = 40009
ADD_SN = 40023
ADD_SWVER = 40041
ADD_SET_TIME = 40399
ADD_SET_POWER = 40599
ADD_STATUS = 40799
ADDR_ACT_POWER = 40800
ADDR_ENERGY = 40804
ADDR_TEMP = 40808

running = True

def signal_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_power_data():
    url = f"http://{SMART_METER_IP}/getLastData?user={USER}&password={PASS}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        inpower = outpower = 0
        if '"1.7.0":"' in data:
            inpower = int(data.split('"1.7.0":"')[1].split('"')[0])
        if '"2.7.0":"' in data:
            outpower = int(data.split('"2.7.0":"')[1].split('"')[0])
        return inpower, outpower
    except Exception as e:
        print(f"Failed to get power data: {e}")
        return 0, 0

def read_registers(client, address, count):
    result = client.read_holding_registers(address, count)
    if not result.isError():
        return result.registers
    else:
        print(f"Modbus error reading addr {address}: {result}")
        return None

def write_registers(client, address, values):
    result = client.write_registers(address, values)
    if result.isError():
        print(f"Modbus write error to addr {address}: {result}")

def int16(val):
    return val & 0xFFFF

def int32_from_registers(regs):
    return (regs[0] << 16) + regs[1]

def int64_from_registers(regs):
    return (regs[0] << 48) + (regs[1] << 32) + (regs[2] << 16) + regs[3]

def prepare_csv_file():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(CSV_PATH, f"ohmpilotdata_{today}.csv")
    os.makedirs(CSV_PATH, exist_ok=True)
    if not os.path.exists(filename):
        with open(filename, "x") as f:
            f.write("Date\tTime\tTemp\tIn Power\tOut Power\tHeater act Power\tHeater set Power\n")
    return filename

def append_csv(filename, temp, in_pwr, out_pwr, act_pwr, set_pwr):
    now = datetime.datetime.now().strftime("%d.%m.%Y\t%H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"{now}\t{temp:.1f}\t{in_pwr}\t{out_pwr}\t{act_pwr}\t{set_pwr}\n")

# Main loop
client = ModbusTcpClient(MB_SERVER)
if not client.connect():
    print(f"Failed to connect to Modbus server at {MB_SERVER}")
    exit(1)

csv_file = prepare_csv_file()
set_value_old = 0
loop_counter = 0
cycle_reset = (TIME_INTERVAL_HOURS * 3600) // SLEEP_SECONDS

try:
    while running:
        if loop_counter % cycle_reset == 0:
            print("Synchronizing time...")
            now = int(time.time())
            out_regs = [(now >> 16) & 0xFFFF, now & 0xFFFF]
            write_registers(client, ADD_SET_TIME + 2, out_regs)

        status_regs = read_registers(client, ADD_STATUS, 10)
        if not status_regs:
            write_registers(client, ADD_SET_POWER, [0, 0])
            continue

        actpower = int32_from_registers(status_regs[ADDR_ACT_POWER - ADD_STATUS:])
        temp_raw = status_regs[ADDR_TEMP - ADD_STATUS]
        temp_corr = (temp_raw / 10.0) * TEMP_K + TEMP_D

        # in_pwr, out_pwr = get_power_data()
        in_pwr, out_pwr = 1000, 500
        # unused_power = out_pwr - in_pwr
        unused_power = 500

        set_value = 0
        if temp_corr < MAX_TEMP:
            set_value = max(0, actpower + unused_power - RESERVED_POWER)
            if set_value < MIN_HEATER_POWER:
                set_value = 0
            elif set_value_old >= MIN_HEATER_POWER and abs(set_value - set_value_old) < MIN_SET_POWER_CHANGE:
                set_value = set_value_old

        set_value_old = set_value
        print(f"Set heater power to {set_value} W")
        write_registers(client, ADD_SET_POWER, [(set_value >> 16) & 0xFFFF, set_value & 0xFFFF])

        power_regs = read_registers(client, ADD_SET_POWER, 2)
        outpower = int32_from_registers(power_regs) if power_regs else 0

        append_csv(csv_file, temp_corr, in_pwr, out_pwr, actpower, outpower)
        time.sleep(SLEEP_SECONDS)
        loop_counter += 1

finally:
    write_registers(client, ADD_SET_POWER, [0, 0])  # Heater off
    client.close()
    print("Modbus connection closed.")
