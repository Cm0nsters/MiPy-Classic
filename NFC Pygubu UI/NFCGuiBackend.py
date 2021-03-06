#Update this to prevent code from auto converting certain hex to ascii (example is serial numer/anticollision)

import serial
from serial.tools import list_ports
import io
import time
import CardSectorData

ser = serial.Serial()

NFCProt = {
    "beep": b'\x02\x13\x15',
    "anticollision": b'\x02\x03\x05',
    "card-check": b'\x03\x02\x00\x05',
    "card-found": b'\x03\x02\x01\x06',
    "no-card-found": b'\x02\x01\x03',
    "manufacture-data": b'\x0A\x05\x00\x03\xFF\xFF\xFF\xFF\xFF\xFF\x0C',
    #Starter has no known listing in the protocol. Will write proper name when ready
    "starter": b'\x03\x0A\x00\x0D'
}

currentDevice = None
connectedDevices = []
currentNFCKey = b'\xFF\xFF\xFF\xFF\xFF\xFF'
beepEnabled = 1
data = None

def startCode():
    print("WARNING: Not all data shown in console is accurate due to python and pyserial automatically converting some hex data")
    listDevice()
    if len(connectedDevices) > 0:
        print("Devices found!")
        print("Connected devices: " + str(connectedDevices))
        setDevice(connectedDevices[0])
        print("Using device: %s" % currentDevice)
    else:
        print("No devices found!")

def listDevice():
    global connectedDevices
    comlist = serial.tools.list_ports.comports()
    for element in comlist:
        connectedDevices.append(element.device)

def setDevice(device):
    global currentDevice
    currentDevice = str(device)

def serialOpen():
    ser.port = str(currentDevice)
    ser.baudrate = 9600
    ser.open()

def beepControl():
    global beepEnabled
    if beepEnabled == 1:
        beepEnabled = 0
        print("NFC Speaker disabled")
    elif beepEnabled == 0:
        beepEnabled = 1
        print("NFC Speaker enabled")

def beep():
    if beepEnabled == 1:
        ser.write(NFCProt["beep"])
        time.sleep(0.25)

def beeptest():
    if beepEnabled == 0:
        print("NFC Speaker beeps are disabled!")
    elif beepEnabled == 1:
        serialOpen()
        ser.write(NFCProt["beep"])
        print("Beep!")
        ser.close()

def passChange(key=None):
    global currentNFCKey
    currentNFCKey = None #put code to manage key data

def cardCheck():
    ser.write(NFCProt["card-check"])
    check = ser.read(3)
    if check == NFCProt["no-card-found"]:
        print("No Card Found. Aborting...")
        ser.close()
    else:
        print("Card Found")
        time.sleep(0.25)

def anticollision():
    serialOpen()
    cardCheck()
    ser.write(NFCProt["anticollision"])
    time.sleep(0.25)
    resp = ser.read(8)
    print(resp[3:])
    beep()
    ser.close()

def manufacture():
    global data
    serialOpen()
    cardCheck()
    ser.write(NFCProt["starter"])
    ser.read(8)
    time.sleep(0.25)
    ser.write(NFCProt["manufacture-data"])
    ser.read(3)
    time.sleep(0.25)
    ser.write(b'\x03\x06\x00\x09')
    resp = ser.read(19)
    data = resp
    print(resp[3:])
    beep()
    ser.close()

def readsector(sector=None,block=None):
    #Sector and Block Pick
    sectorChoose =  CardSectorData.sec[sector]
    blockChoose = CardSectorData.secblock[sector]
    blockIDEnding = CardSectorData.secreadend
    blockIDMid = CardSectorData.secreadstart
    byteread = bytearray()
    bytekeygen1 = bytearray([0x0A,0x05])
    bytekeygen2 = bytearray([0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
    bytekeygen = bytearray()
    
    #byteread
    byteread.extend('\x03\x06'.encode('utf-8'))
    byteread.extend(sectorChoose[block].encode('utf-8'))
    byteread.extend(blockChoose[block].encode('utf-8'))
    
    #bytekeygen1
    bytekeygen1.extend(blockIDMid[sector].encode('utf-8'))
    
    #bytekeygen2
    bytekeygen2.extend(blockIDEnding[sector].encode('utf-8'))

    #bytekeygen
    bytekeygen.extend(bytekeygen1)
    bytekeygen.extend(bytekeygen2)

    #Beginning of card read
    serialOpen()
    cardCheck()
    ser.write(NFCProt["starter"])
    ser.read(8)
    time.sleep(0.25)
    ser.write(bytekeygen)
    ser.read(3)
    time.sleep(0.25)
    ser.write(byteread)
    resp = ser.read(19)
    print(resp[3:])
    beep()
    ser.close()

#DONT USE THIS COMMAND IT IS NOT FUNCTIONAL
def writesector(sector=None,block=None,hexinput=None):
    resp = None
    
    #Sector and Block Pick
    blockIDEnding = CardSectorData.secreadend
    blockIDMid = CardSectorData.secreadstart
    bytekeygen1 = bytearray([0x0A,0x05])
    bytekeygen2 = bytearray([0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
    bytekeygen = bytearray()

    #bytekeygen1
    bytekeygen1.extend(blockIDMid[sector].encode('utf-8'))
    
    #bytekeygen2
    bytekeygen2.extend(blockIDEnding[sector].encode('utf-8'))

    #bytekeygen
    bytekeygen.extend(bytekeygen1)
    bytekeygen.extend(bytekeygen2)

    serialOpen()
    cardCheck()
    ser.write(NFCProt["starter"])
    resp = ser.read(8)
    print(resp)
    time.sleep(0.25)
    ser.write(bytekeygen)
    resp = ser.read(3)
    print(resp)
    time.sleep(0.25)
    #Create code to change location of write and content of write
    #Re-analyze protocol via ASPMon to find out how to write different text
    ser.write(b'\x13\x07\x01\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\xB4')
    resp = ser.read(3)
    print(resp)
    beep()
    ser.close()

#Console CMD Runner
startCode()
