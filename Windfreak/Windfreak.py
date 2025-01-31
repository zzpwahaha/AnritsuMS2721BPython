from windfreak import SynthHD
from time import sleep

synth = SynthHD("COM11")
synth.init()

synth.reference_mode = "external"
synth.reference_frequency = 10e6
synth[0].channel_spacing = 10

synth[0].select()  # select to channel 0
synth._write("b1")  # turn on Ref Doubler
synth._write("U9")  # set charge pump current to 9
print(synth._query("b?"))
print(synth._query("U?"))


# Set channel 0 power and frequency
synth[0].power = 17.0 # dBm
synth[0].frequency = 6834.6820000*1e6 # Hz
synth[0].phase = 0

# Enable channel 0
synth[0].enable = True

print(synth[0].frequency)
print(synth[0].power)
print(synth[0].lock_status)

sleep(100)
