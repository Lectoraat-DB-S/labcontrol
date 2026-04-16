import serial
import time
ser = serial.Serial('COM9', 38400, timeout=0, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO,  rtscts=1)
space = 0x20
carrreturn = 0x0D
ser.write(b" \r\n")
time.sleep(0.1)
line = ser.readline()
while(line != b'\x00'):
    line = ser.readline()
    print(line)
    time.sleep(0.1)
time.sleep(1)   
ser.write(b"*IDN?\r\n")
line = ser.readline()
print(line)
line2 = ser.readline()
print(line2)
while(True):
    line2 = ser.readline()
    print(line2)
    time.sleep(0.5)
    
