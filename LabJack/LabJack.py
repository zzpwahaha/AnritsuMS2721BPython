import sys
sys.path.append('C:\Chimera\LabJackPython\build\lib')

import u3  # Import the LabJack U3 class (for U3 devices)


class LabJackReader:
    def __init__(self, device_type="U3", connection="USB", port=0):
        """
        Initializes the connection to the LabJack device.
        
        :param device_type: The type of the LabJack device (e.g., 'U3', 'T7', etc.)
        :param connection: The connection type (e.g., 'USB', 'Ethernet', etc.)
        :param port: The port number for the connection (for Ethernet or other connections)
        """
        self.device_type = device_type
        self.connection = connection
        self.port = port
        self.device = None
        
        # Initialize the LabJack device
        self.connect()

    def connect(self):
        """
        Establish a connection to the LabJack device.
        """
        try:
            if self.device_type == "U3":
                self.device = u3.U3()  # Use the LabJack U3 device class
            else:
                print(f"Device type {self.device_type} not supported in this example.")
                return
            # self.device.openLabJack(self.connection, self.port)
            # Get the calibration constants from the U6, otherwise default nominal values
            # will be be used for binary to decimal (analog) conversions.
            self.device.getCalibrationData()
            # Configure all FIO0-FIO7 to analog inputs (255 = b11111111).
            self.device.configIO(FIOAnalog=255)
            print(f"Connected to LabJack device via {self.connection}.")
        except Exception as e:
            print(f"Error connecting to LabJack device: {e}")

    def read_voltage(self, channel=0):
        """
        Reads the voltage value from a specific analog input channel.
        
        :param channel: The channel number to read from (default is 0)
        :return: The voltage reading from the channel.
        """
        try:
            # Read the voltage on the specified channel (e.g., channel 0 for AIN0)
            voltage = self.device.getAIN(channel, longSettle=True, quickSample=False)
            return voltage
        except Exception as e:
            print(f"Error reading voltage from channel {channel}: {e}")
            return None

    def close(self):
        """
        Closes the connection to the LabJack device.
        """
        if self.device:
            self.device.close()
            print("Connection to LabJack device closed.")
        else:
            print("No device to close.")

# Example usage:
if __name__ == "__main__":
    lj_reader = LabJackReader(device_type="U3")
    channel = 4
    # for channel in range(8):
    #     voltage = lj_reader.read_voltage(channel=channel)  # Read voltage from AIN0
    #     if voltage is not None:
    #         print(f"Voltage on channel {channel:d}: {voltage:.4f} V")
    voltage = lj_reader.read_voltage(channel=channel)  # Read voltage from AIN0
    if voltage is not None:
        print(f"Voltage on channel {channel:d}: {voltage:.4f} V")

    lj_reader.close()
