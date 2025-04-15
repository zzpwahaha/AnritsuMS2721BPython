import socket
import time
import numpy as np

class SiglentScopeSocket:
    def __init__(self, ip_address, port=5025, timeout=5, buffer_size=4096):
        self.ip = ip_address
        self.port = port
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.sock = None
        self.header_len = 11  # Length of waveform header (#800002000)
        
    def connect(self):
        """Establish socket connection to the oscilloscope"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip, self.port))
            
            # Read initial connection message
            print("Connection message:", self._recv_all())
            
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.ip}:{self.port}") from e

    def disconnect(self):
        """Close the socket connection"""
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, command):
        """Send SCPI command to the oscilloscope"""
        try:
            self.sock.sendall(command.encode('ascii') + b'\n')
            time.sleep(0.1)  # Short delay for command processing
        except socket.error as e:
            raise ConnectionError("Command send failed") from e

    def query(self, command):
        """Send query and return response"""
        self.send(command)
        return self._recv_all()

    def _recv_all(self):
        """Receive all available data from socket"""
        data = b''
        while True:
            try:
                part = self.sock.recv(self.buffer_size)
                if not part:
                    break
                data += part
                if len(part) < self.buffer_size:
                    break  # Assume complete message received
            except socket.timeout:
                break
        return data.decode('ascii').strip()

    def _parse_numeric_response(self, response):
        """Parse oscilloscope responses containing values with units"""
        try:
            # Split on whitespace and take the last part before unit
            parts = response.strip().split()
            if not parts:
                return 0.0
            
            # Get the numerical part (could be in second position)
            value_str = parts[-1] if len(parts) > 1 else parts[0]
            
            # Remove any trailing non-numeric characters (units)
            while value_str and not value_str[-1].isdigit():
                value_str = value_str.rstrip(value_str[-1])
                
            return float(value_str)
        
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse numeric value from: '{response}'") from e

    def get_waveform(self, channel=1, points=1000):
        """
        Retrieve waveform data from specified channel
        Returns: (time_array, voltage_array, metadata)
        """
        # Configure acquisition
        self.send(f":STOP")
        self.send(f":WAV:SOUR C{channel}")
        self.send(":WAV:FORM BYTE")  # 8-bit binary format
        self.send(f":WAV:POIN {points}")
        
        # Trigger single acquisition
        self.send(":SINGLE")
        while ":TRIG:STAT?" in self.query(":TRIG:STAT?"):
            time.sleep(0.1)

        # Get waveform parameters
        vdiv = self._parse_numeric_response(self.query(f":C{channel}:VOLT_DIV?"))
        offset = self._parse_numeric_response(self.query(f":C{channel}:OFFSET?"))
        tdiv = self._parse_numeric_response(self.query(":TIM:MAIN:SCAL?"))
        samp_rate = self._parse_numeric_response(self.query(":ACQ:SRAT?"))

        # Get raw waveform data
        self.send(":WAV:DATA?")
        raw_data = self._get_binary_data()
        
        # Convert to voltage values
        y_origin = self._parse_numeric_response(self.query(":WAV:YOR?"))
        y_ref = self._parse_numeric_response(self.query(":WAV:YREF?"))
        y_inc = self._parse_numeric_response(self.query(":WAV:YINC?"))
        voltages = (np.array(raw_data) - y_origin - y_ref) * y_inc + offset
        
        # Create time array
        x_inc = self._parse_numeric_response(self.query(":WAV:XINC?"))
        time_array = np.arange(0, len(voltages)) * x_inc
        time_array -= float(self.query(":TIM:OFFS?"))  # Adjust trigger position
        
        metadata = {
            'channel': channel,
            'vdiv': vdiv,
            'offset': offset,
            'tdiv': tdiv,
            'sample_rate': samp_rate,
            'points': len(voltages)
        }
        
        return time_array, voltages, metadata

    def _get_binary_data(self):
        """Handle binary waveform data transfer"""
        # Read header to determine data length
        all_recv = self._recv_all()
        header = all_recv[:self.header_len].decode('ascii')
        header = header.split(',')[1]
        data_size = int(header[1:])
        
        # Read binary data
        raw_data = bytearray()
        while len(raw_data) < data_size:
            remaining = data_size - len(raw_data)
            raw_data += self.sock.recv(min(remaining, self.buffer_size))
        
        return list(raw_data)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# Usage example
if __name__ == "__main__":
    SCOPE_IP = "6.1.1.92"  # Replace with your scope's IP
    
    with SiglentScopeSocket(SCOPE_IP) as scope:
        # Get identification
        print("IDN:", scope.query("*IDN?"))
        
        # Capture waveform from channel 1
        t, v, meta = scope.get_waveform(channel=1)
        
        print(f"Captured {meta['points']} points at {meta['sample_rate']/1e6:.2f} MS/s")
        print(f"Vertical scale: {meta['vdiv']} V/div")
        
        # Plotting example
        import matplotlib.pyplot as plt
        plt.plot(t, v)
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.title("Oscilloscope Waveform")
        plt.grid(True)
        plt.show()