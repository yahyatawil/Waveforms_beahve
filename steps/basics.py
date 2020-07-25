from behave import *
from ctypes import *
from dwfconstants import *
import time
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")
    
    
hdwf = c_int()

cRX = c_int(0)
fParity = c_int(0)
rgRX = create_string_buffer(8193)

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

@given('Analog Discovery 2 is connected')
def step_impl(context):
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
    assert hdwf.value != hdwfNone.value,"Check USB connection with AD2"

@when('Output #{output_number} set to {output_state}')
def step_impl(context,output_number,output_state):
    # enable output/mask on 8 LSB IO pins, from DIO 0 to 7
    IO_enable_mask = 0x0000 | (1 << int(output_number))
    IO_state_mask = 0x0000 | (int(output_state)<<int(output_number)) 
    dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(IO_enable_mask)) 
    # set value on enabled IO pins
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(IO_state_mask)) 

@then('Input #{input_number} is {input_state}')
def step_impl(context,input_number,input_state): 
    dwRead = c_uint32()
    # fetch digital IO information from the device 
    dwf.FDwfDigitalIOStatus (hdwf) 
    # read state of all pins, regardless of output enable
    dwf.FDwfDigitalIOInputStatus(hdwf, byref(dwRead)) 
    assert  bin(dwRead.value)[2:].zfill(16)[15-int(input_number)] == input_state,[dwf.FDwfDeviceCloseAll(),"Input is not matching output"][1]
    
    
    
@given('Analog Discovery 2 UART is configured') 
def step_impl(context):   
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
    assert hdwf.value != hdwfNone.value,"Check USB connection with AD2"
    dwf.FDwfDigitalUartRateSet(hdwf, c_double(9600)) # 9.6kHz
    dwf.FDwfDigitalUartRxSet(hdwf, c_int(2)) # RX = DIO-2
    dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
    dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 none, 1 odd, 2 even
    dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length

@then('Wait to send 0x{rx_char} via UART')
def step_impl(context,rx_char):
    dwf.FDwfDigitalUartRx(hdwf, None, c_int(0), byref(cRX), 0)# initialize RX reception
    time.sleep(1)
    print("Receiving on RX, press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(0.001)
            dwf.FDwfDigitalUartRx(hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), 0) # read up to 8k chars at once
            if cRX.value > 0:
                rgRX[cRX.value] = 0 # add zero ending
                #sz = rgRX.value.decode()
                #print(sz, end = '', flush=True) # works with CR+LF or LF
                if(int.from_bytes(rgRX.value, "little") == int(rx_char,16)):
                    break
    except KeyboardInterrupt: # Ctrl+C
        pass

@then('Close connection with Analog Discovery 2') 
def step_impl(context):
    dwf.FDwfDeviceCloseAll()    
