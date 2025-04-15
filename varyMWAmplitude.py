from Windfreak.Windfreak import WindfreakInitializer
from AnritsuMS2712B.AnritsuMS2721B import AnritsuMS2721B
from LabJack.LabJack import LabJackReader
from datetime import datetime
import csv
import time
import numpy as np

WINFREAK_CONFIG = {
    'port': 'COM11',
    'reference_mode': 'external',
    'reference_frequency': 10e6,
    'channel_spacing': 10
}
LABJACK_CHANNEL = 4


# Windfreak
wf = WindfreakInitializer(**WINFREAK_CONFIG)
wf.connect()
wf.configure_device()
# Configure channel 0
wf.configure_channel(
    channel=0,
    power=17.0,
    frequency=6834.682e6,
    phase=0,
    enable=True
)

# Get and print status
status = wf.get_status(0)
print("Windfreak Status:")
print(f"\tFrequency: {status['frequency']} Hz")
print(f"\tPower: {status['power']} dBm")
print(f"\tLock Status: {status['lock_status']}")
print(f"\tReference Doubler: {status['reference_doubler']}")
print(f"\tCharge Pump: {status['charge_pump']}")


# Anritsu
sa = AnritsuMS2721B('TCPIP::6.1.1.91::inst0::INSTR')
print(f"Anritsu Connected to: {sa.get_idn()}")
print(f"\tMarker 1 amplitude: {sa.get_marker_y(1)} dBm")

# Labjack
lj_reader = LabJackReader(device_type="U3")
voltage = lj_reader.read_voltage(channel=LABJACK_CHANNEL)  # Read voltage from AIN4
if voltage is not None:
    print(f"\tVoltage on channel {LABJACK_CHANNEL:d}: {voltage:.4f} V")




# Define the column headers (this will be written only once)
columns = ['time', 'output MW power (dBm)', 'PD DC voltage (V)', 'PD MW power (dBm)']

# Open the file in append mode so that data is added continuously
with open('varyMWAmplitude.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    
    # Write header only if the file is empty (i.e., it's the first time opening it)
    if file.tell() == 0:
        writer.writerow(columns)
    
    windfreak_power = np.linspace(-10,16,27)
    average_num = 60

    # Start collecting data continuously 
    for wfp in windfreak_power:
        wf.synth[0].power = wfp
        time.sleep(1)
        for _ in range(average_num):  # You can replace 10 with a condition for continuous collection
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the time as YYYY-MM-DD HH:MM:SS

            output_mw_power = wfp
            dc_voltage = lj_reader.read_voltage(channel=LABJACK_CHANNEL)  # Read voltage from AIN4, V
            mw_power = sa.get_marker_y(1) #dBm
            
            # Prepare the row to be written
            row = [current_time, output_mw_power, dc_voltage, mw_power]
            
            # Write the row to the CSV file
            writer.writerow(row)

            # Flush the file buffer to ensure data is written immediately
            file.flush()
            