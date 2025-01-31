# Anritsu
Install the VISA by installing the **Anritsu Software Tool Box** from [here](https://www.anritsu.com/en-us/test-measurement/support/downloads?model=MST)

Get the programming manual from [here](https://www.anritsu.com/en-us/test-measurement/support/downloads?model=MS2721B) under the `Programming Manual` section.

In the C/C++ example page in the Programming Manual, it specify the ip connection via VISA as:
```
// IdnExample.cpp : Microsoft Visual Studio-Generated Example
// Based on Example 2-1 in the NI-VISA User Manual
// Usage : IdnExample "TCPIP::xxx.xxx.xxx.xxx::inst0::INSTR"
// where xxx.xxx.xxx.xxx is the IP address of the instrument.
```

Using pyvisa, can choose to use USB or TCP. In the USB case, the USB address will show up in `list_resources` as 
```
rm.list_resources()
('USB0::0x0B5B::0xFFF9::1112199_150_11::INSTR')
```
but not for TCP. Need to manually input the TCP address in the format above to open the connection through VISA.

# Windfreak
Install Windfreak related parts using 
```
pip install windfreak
```

# LabJack
Install labjack related parts need to sue 
```
git clone https://github.com/labjack/LabJackPython.git
```
and add the directory to the path after installation as in `LabJack.py`