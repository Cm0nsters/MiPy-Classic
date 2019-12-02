#This copy is being depreciated. Please use NFC2.py for new updates

import serial
import io
import time

#REWRITE TO NOT CRASH ON INCORRECT READ SIZES (USE VARIABLES WITH ser.read(length here))

ser = serial.Serial()

def serialOpen():
    ser.port = 'COM4'
    ser.baudrate = 9600
    ser.open()

def beep():
    serialOpen()
    buffer = bytearray([0x02,0x13,0x15])
    print(buffer)
    ser.write(buffer)
    print(ser.read(size=len(buffer)))
    ser.close()

def serialnumber():
    serialOpen()
    buffer = b'\x03\x02\x00\x05'
    ser.write(buffer)
    resp = ser.read(4)
    if resp == b'\x02\x01\x03':
        print("No card found, closing...")
        ser.close()
    else:
        buffer = b'\x02\x03\x05\x00'
        ser.write(buffer)
        resp = ser.read(7)
        print(resp)
        ser.close()

def test():
    serialOpen()
    #Select Card
    buffer = bytearray([0x02,0x04,0x06])
    ser.write(buffer)
    print(ser.read(size=3))
    time.sleep(0.25)
    #Verify Key
    buffer = bytearray([0x04,0x05,0x01,0x03,0x0A])
    ser.write(buffer)
    print(ser.read(size=3))
    time.sleep(0.25)
    #Write data to Sector 1, Block 0
    buffer = bytearray([0x13,0x07,0x04,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x2E])
    ser.write(buffer)
    print(ser.read(size=3))
    time.sleep(0.25)
    ser.write(bytearray([0x02,0x13,0x15]))
    ser.close()

while True:
    command = input("Command:")
    if command == "beep":
        beep()
    elif command == "serialnumber":
        serialnumber()
    elif command =="test":
        test()
    elif command == "exit":
        print("Exiting...")
        break
    else:
        print("Command error! Invalid command!")