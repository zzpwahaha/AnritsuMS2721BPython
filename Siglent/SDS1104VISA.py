import pyvisa
import time

class SiglentScope:
    def __init__(self, visa_address):
        self.visa_address = visa_address
        self.rm = pyvisa.ResourceManager()
        self.instr = None
        self._sara_units = {'G': 1e9, 'M': 1e6, 'k': 1e3}

    def connect(self):
        """Establish connection and configure basic settings"""
        try:
            self.instr = self.rm.open_resource(self.visa_address)
            self.instr.write("chdr off")  # Disable header in responses
            self.instr.timeout = 30000    # Extended timeout for large transfers
            self.instr.chunk_size = 20 * 1024 * 1024  # 20 MB buffer
        except pyvisa.VisaIOError as e:
            raise ConnectionError(f"Failed to connect to {self.visa_address}") from e

    def disconnect(self):
        """Close the connection"""
        if self.instr:
            self.instr.close()
            self.instr = None

    def _parse_parameter(self, response):
        """Parse numerical parameters from oscilloscope responses"""
        try:
            # Split into parts and take last numerical value
            parts = response.strip().split()
            value_str = parts[-1] if len(parts) > 1 else parts[0]
            
            # Remove non-numeric characters from end
            while value_str and not value_str[-1].isdigit() and value_str[-1] not in {'.', '+', '-', 'e', 'E'}:
                value_str = value_str[:-1]
                
            return float(value_str)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse value from: '{response}'") from e

    def _parse_sara(self, sara_response):
        """Parse sample rate with unit conversion"""
        for unit, multiplier in self._sara_units.items():
            if unit in sara_response:
                parts = sara_response.split(unit)
                return float(parts[0]) * multiplier
        return float(sara_response)

    def get_waveform(self, channel=1):
        """Acquire and process waveform data from specified channel"""
        if not self.instr:
            raise ConnectionError("Not connected to oscilloscope")

        try:
            # Query parameters
            vdiv = self._parse_parameter(self.instr.query(f"c{channel}:vdiv?"))
            ofst = self._parse_parameter(self.instr.query(f"c{channel}:ofst?"))
            tdiv = self._parse_parameter(self.instr.query("tdiv?"))
            sara = self._parse_sara(self.instr.query("sara?"))

            # Trigger waveform acquisition
            self.instr.write(f"c{channel}:wf? dat2")
            raw_data = self.instr.read_raw()

            # Process raw data
            header_size = 15  # Adjust based on actual header length
            data_bytes = list(raw_data[header_size:-2])  # Remove header and termination
            
            # Convert bytes to voltage values
            volt_value = []
            for byte in data_bytes:
                # Handle two's complement for signed values
                if byte > 127:
                    byte -= 256
                volt_value.append(byte / 25 * vdiv - ofst)

            # Generate time array
            time_value = []
            for idx in range(len(volt_value)):
                time_data = -(tdiv * 14 / 2) + idx * (1 / sara)
                time_value.append(time_data)

            return time_value, volt_value

        except pyvisa.VisaIOError as e:
            raise OscilloscopeError(f"Waveform acquisition failed: {str(e)}") from e

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

class OscilloscopeError(Exception):
    pass

# Usage example
if __name__ == "__main__":
    VISA_ADDRESS = "TCPIP::6.1.1.92::INSTR"  # Replace with your scope's address
    
    try:
        with SiglentScope(VISA_ADDRESS) as scope:
            # Acquire waveform from channel 1
            time_data, volt_data = scope.get_waveform(channel=1)
            
            # Print first 10 samples
            print("Time (s)\tVoltage (V)")
            for t, v in zip(time_data[:10], volt_data[:10]):
                print(f"{t:.6e}\t{v:.4f}")

    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except OscilloscopeError as e:
        print(f"Oscilloscope error: {str(e)}")