#Update this to prevent code from auto converting certain hex to ascii (example is serial numer/anticollision)

import serial
from serial.tools import list_ports
import io
import time
import CardSectorData
import HelpList

ser = serial.Serial()

NFCProt = {
    "beep": b'\x02\x13\x15',
    "anticollision": b'\x02\x03\x05',
    "card-check": b'\x03\x02\x00\x05',
    "card-found": b'\x03\x02\x01\x06',
    "no-card-found": b'\x02\x01\x03',
    "manufacture-data": b'\x0A\x05\x00\x03\xFF\xFF\xFF\xFF\xFF\xFF\x0C',
    "card-key-valid": b'\x02\x05\x07',
    "write-success": b'\x02\x07\x09',
    #Starter has no known listing in the protocol. Will write proper name when ready
    "starter": b'\x03\x0A\x00\x0D'
}

currentDevice = None
connectedDevices = []
currentNFCKey = b'\xFF\xFF\xFF\xFF\xFF\xFF'
beepEnabled = 1

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

#WIP, MAY BE BUGGY
def passChange(key=None):
    global currentNFCKey
    currentNFCKey = key

def cardCheck():
    ser.write(NFCProt["card-check"])
    check = ser.read(3)
    if check == NFCProt["no-card-found"]:
        print("No Card Found. Aborting...")
        ser.close()
        exit()
    else:
        print("Card Found")
        time.sleep(0.25)

def keyCheck():
    ser.write(currentNFCKey)
    keyResp = ser.read(3)
    if keyResp == NFCProt["card-key-valid"]:
        pass
    else:
        print("This key is invalid!")
        exit()

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
    print(resp[3:])
    beep()
    ser.close()

def readsector(sector=None,block=None):
    #Sector and Block Pick
    #readbyte
    readbyte = bytearray([0x03,0x06])
    byte1 = CardSectorData.sec[sector]
    byte2 = CardSectorData.secreadblock[sector]
    readbyte.extend(byte1[block])
    readbyte.extend(byte2[block])

    #bytekey
    bytekeyfinal = bytearray()
    bytekey1 = bytearray([0x0A,0x05])
    bytekey2 = bytearray(b'\x03%s' %currentNFCKey)
    bytekey1.extend(CardSectorData.seckeystart[sector])
    bytekey2.extend(CardSectorData.seckeyend[sector])
    bytekeyfinal.extend(bytekey1)
    bytekeyfinal.extend(bytekey2)

    #Beginning of card read
    serialOpen()
    cardCheck()
    ser.write(NFCProt["starter"])
    ser.read(8)
    time.sleep(0.25)
    ser.write(bytekeyfinal)
    ser.read(3)
    time.sleep(0.25)
    ser.write(readbyte)
    resp = ser.read(19)
    print(resp[3:])
    beep()
    ser.close()

#DONT USE THIS COMMAND IT IS NOT FUNCTIONAL
def writesector(sector,block,data):
    #writebyte (THIS MAY NOT WORK AS A BYTEARRAY)
    writebyte = bytearray([0x13,0x07])
    byte1 = CardSectorData.sec[sector]
    byte2 = 0
    writebyte.extend(byte1[block])
    
    #write blank to card
    if data == b'':
        writebyte.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    else:
        writebyte.extend(data)

    #bytekey
    bytekeyfinal = bytearray()
    bytekey1 = bytearray([0x0A,0x05])
    bytekey2 = bytearray([0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
    bytekey1.extend(CardSectorData.seckeystart[sector])
    bytekey2.extend(CardSectorData.seckeyend[sector])
    bytekeyfinal.extend(bytekey1)
    bytekeyfinal.extend(bytekey2)

    serialOpen()
    cardCheck()

    #bruteforce write
    for i in range(256):
        ser.write(NFCProt["starter"])
        ser.read(8)
        time.sleep(0.03125)
        ser.write(bytekeyfinal)
        time.sleep(0.03125)
        writebyte.append(byte2)
        ser.write(writebyte)
        resp=ser.read(3)
        print("%s returned %s" %(writebyte,resp))
        byte2 += 1
        del writebyte[-1]
        time.sleep(0.03125)
    
    print("Bruteforce Complete!")
    beep()
    ser.close()

#Console CMD Runner
startCode()
while True:
    command = input("Command:")
    if command[:5] == "help" or command[:5] == "help ":
        HelpList.helpCommand(command[5:])
    elif command == "setdevice":
        device = input("Device Name:")
        setDevice(device)
    elif command == "devicename":
        print("Using device: %s" % currentDevice)
    elif command == "beeptoggle":
        beepControl()
    elif command == "beep":
        beeptest()
    elif command == "changekey":
        print("Sorry! This feature is not yet implemented!")
        #key = input("New Key:")
        #passChange(key)
        #print("New key set to: %s" % currentNFCKey)
    elif command == "": #use for different key choices (key a or b)
        pass
    elif command == "anticollision":
        anticollision()
    elif command == "manufacture":
        manufacture()
    elif command == "sectorread":
        sect = input("Sector:")
        block = input("Block:")
        readsector(int(sect),int(block))
    elif command == "sectorwrite":
        sect = input("Sector:")
        block = input("Block:")
        data = input("Data:")
        writesector(int(sect),int(block),bytes(data.encode('utf-8')))
    elif command == "exit":
        print("Exiting...")
        break
    else:
        print("Invalid command! Use 'help' to get started")