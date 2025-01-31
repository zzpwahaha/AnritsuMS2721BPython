import pyvisa

# Create a resource manager
rm = pyvisa.ResourceManager()

# List available resources
print(rm.list_resources()) 

ins = rm.open_resource('TCPIP::6.1.1.91::inst0::INSTR')

print(ins.query('*idn?'))

print(ins.query(':CALC:MARKER1:Y?'))

