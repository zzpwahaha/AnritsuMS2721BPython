import pyvisa

class AnritsuMS2721B:
    def __init__(self, address, resource_manager=None, timeout=5000):
        """
        Initialize connection to Anritsu MS2721B
        
        :param address: VISA resource address (e.g., 'TCPIP::192.168.1.1::INSTR')
        :param resource_manager: Optional existing pyvisa ResourceManager
        :param timeout: Communication timeout in milliseconds
        """
        self.address = address
        self.rm = resource_manager or pyvisa.ResourceManager()
        self.instrument = None
        self.timeout = timeout
        
        try:
            self.instrument = self.rm.open_resource(self.address)
            self.instrument.timeout = self.timeout
        except pyvisa.VisaIOError as e:
            raise ConnectionError(f"Failed to connect to {self.address}") from e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the VISA connection"""
        if self.instrument:
            self.instrument.close()
            self.instrument = None

    def get_idn(self):
        """Get instrument identification string"""
        return self._query('*IDN?')

    def get_marker_y(self, marker=1):
        """
        Get current marker Y-value (amplitude)
        
        :param marker: Marker number (1-4)
        :return: Amplitude in dBm
        """
        return float(self._query(f':CALC:MARKER{marker}:Y?'))

    def _query(self, command):
        """Send query and return stripped response"""
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        return self.instrument.query(command).strip()

    def _write(self, command):
        """Send command without response"""
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        self.instrument.write(command)

    @staticmethod
    def list_resources():
        """List available VISA resources"""
        return pyvisa.ResourceManager().list_resources()

# Example usage
if __name__ == "__main__":
    with AnritsuMS2721B('TCPIP::6.1.1.91::inst0::INSTR') as sa:
        print(f"Connected to: {sa.get_idn()}")
        print(f"Marker 1 amplitude: {sa.get_marker_y(1)} dBm")