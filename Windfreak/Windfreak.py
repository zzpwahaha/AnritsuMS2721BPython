from windfreak import SynthHD
from time import sleep

from windfreak import SynthHD
from time import sleep

class WindfreakInitializer:
    def __init__(self, port, reference_mode='external', reference_frequency=10e6, 
                 channel_spacing=10, init_delay=1.0):
        """
        Initialize Windfreak Synthesizer
        :param port: COM port (e.g., 'COM11')
        :param reference_mode: 'internal' or 'external'
        :param reference_frequency: Reference frequency in Hz
        :param channel_spacing: Channel spacing in Hz
        :param init_delay: Initialization delay in seconds
        """
        self.port = port
        self.reference_mode = reference_mode
        self.reference_frequency = reference_frequency
        self.channel_spacing = channel_spacing
        self.init_delay = init_delay
        self.synth = None
        self._connected = False

    def connect(self):
        """Establish connection and initialize device"""
        try:
            self.synth = SynthHD(self.port)
            self.synth.init()
            sleep(self.init_delay)  # Allow time for initialization
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.port}") from e

    def configure_device(self):
        """Configure global device settings"""
        if not self._connected:
            raise ConnectionError("Device not connected")
            
        # Configure reference settings
        self.synth.reference_mode = self.reference_mode
        self.synth.reference_frequency = self.reference_frequency
        
        # Send low-level commands
        self.synth._write("b1")  # Enable reference doubler
        self.synth._write("U9")  # Set charge pump current
        
        # Configure channel spacing for channel 0
        self.synth[0].channel_spacing = self.channel_spacing

    def configure_channel(self, channel=0, power=17.0, frequency=6834.682e6,
                         phase=0, enable=True):
        """
        Configure a specific channel
        :param channel: Channel index (0 or 1)
        :param power: Output power in dBm
        :param frequency: Frequency in Hz
        :param phase: Phase in degrees
        :param enable: Enable channel output
        """
        if not self._connected:
            raise ConnectionError("Device not connected")
            
        ch = self.synth[channel]
        ch.select()
        ch.power = power
        ch.frequency = frequency
        ch.phase = phase
        ch.enable = enable

    def get_status(self, channel=0):
        """Get channel status information"""
        if not self._connected:
            raise ConnectionError("Device not connected")
            
        ch = self.synth[channel]
        return {
            'frequency': ch.frequency,
            'power': ch.power,
            'phase': ch.phase,
            'enabled': ch.enable,
            'lock_status': ch.lock_status,
            'reference_doubler': self.synth._query("b?"),
            'charge_pump': self.synth._query("U?")
        }

    def disconnect(self):
        """Close connection and cleanup"""
        if self._connected:
            for ch in [0, 1]:
                self.synth[ch].enable = False
            self.synth = None
            self._connected = False

    def __enter__(self):
        self.connect()
        self.configure_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @property
    def is_connected(self):
        return self._connected

# Example usage
if __name__ == "__main__":
    config = {
        'port': 'COM11',
        'reference_mode': 'external',
        'reference_frequency': 10e6,
        'channel_spacing': 10
    }

    with WindfreakInitializer(**config) as wf:
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
        print("Device Status:")
        print(f"Frequency: {status['frequency']} Hz")
        print(f"Power: {status['power']} dBm")
        print(f"Lock Status: {status['lock_status']}")
        print(f"Reference Doubler: {status['reference_doubler']}")
        print(f"Charge Pump: {status['charge_pump']}")


# synth = SynthHD("COM11")
# synth.init()

# synth.reference_mode = "external"
# synth.reference_frequency = 10e6
# synth[0].channel_spacing = 10

# synth[0].select()  # select to channel 0
# synth._write("b1")  # turn on Ref Doubler
# synth._write("U9")  # set charge pump current to 9
# print(synth._query("b?"))
# print(synth._query("U?"))


# # Set channel 0 power and frequency
# synth[0].power = 17.0 # dBm
# synth[0].frequency = 6834.6820000*1e6 # Hz
# synth[0].phase = 0

# # Enable channel 0
# synth[0].enable = True

# print(synth[0].frequency)
# print(synth[0].power)
# print(synth[0].lock_status)

# sleep(100)
