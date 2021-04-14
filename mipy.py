import serial
from serial.tools import list_ports
import io
import time

class Reader:
    def __init__(self,port):
        self.port = port

    def __repr__(self):
        return f"Reader({self.port!r})"

    def __str__(self):
        return f"NFC Reader device using {self.port}"

    ser = serial.Serial()

    nfc_protocol = {
        "beep": b"\x02\x13\x15",
        "anticollision": b"\x02\x03\x05",
        "card-check": b"\x03\x02\x00\x05",
        "card-found": b"\x03\x02\x01\x06",
        "no-card-found": b"\x02\x01\x03",
        "card-key-valid": b"\x02\x05\x07",
        "write-success": b"\x02\x07\x09",
        #Starter has no known listing in the protocol. Will write proper name when ready
        "starter": b"\x03\x0A\x00\x0D"
    }

    beep_enabled = 1
    delay = 0.03125
    card_key = None

    serial_close = lambda self: self.ser.close()
    manufacture = lambda self: self.read_card(0,0)

    def serial_open(self):
        self.ser.port = str(self.port)
        self.ser.baudrate = 9600
        self.ser.open()

    def beep(self):
        if self.beep_enabled == 1:
            self.ser.write(self.nfc_protocol["beep"])
            time.sleep(self.delay)

    def card_check(self):
        self.ser.write(self.nfc_protocol["card-check"])
        check = self.ser.read(3)
        if check == self.nfc_protocol["no-card-found"]:
            print("No Card Found. Aborting...")
            self.serial_close()
        else:
            print("Card Found")
            time.sleep(self.delay)

    def key_check(self):
        self.ser.write(self.card_key)
        keyResp = self.ser.read(3)
        if keyResp != self.nfc_protocol["card-key-valid"]:
            print("This key is invalid!")

    def anticollision(self):
        self.card_check()
        self.ser.write(self.nfc_protocol["anticollision"])
        time.sleep(self.delay)
        resp = self.ser.read(8)
        self.beep()
        return resp[3:]


    def read_card(self,sector,block):
        self.card_check()
        self.ser.write(self.nfc_protocol["starter"])
        self.ser.read(8)
        time.sleep(self.delay)
        self.ser.write(bytearray([0x0A,0x05,int(hex(sector),16),0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,int(hex(sector+12),16)])) #final bytekey
        self.ser.read(3)
        time.sleep(self.delay)
        self.ser.write(bytearray([0x03,0x06,int(hex((4*sector)+block),16),int(hex(9+(4*sector)+block),16)])) #read data
        resp = self.ser.read(19)
        self.beep()
        return resp[3:]

    #TODO - continue reverse engineering and development of writing
    def write_card(self,sector,block,data):
        writebyte = bytearray([0x13,0x07,int(hex((4*sector)+block),16)])
   
        #card data
        if data == b"":
            writebyte.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        elif len(data) != 16:
            return print("Invalid Formatting! Data needs to be 16 characters long!")
        else:
            writebyte.extend(data)

        self.card_check()

        #bruteforce write
        for i in range(256):
            self.ser.write(self.nfc_protocol["starter"])
            self.ser.read(8)
            time.sleep(self.delay)
            self.ser.write(bytearray([0x0A,0x05,int(hex(sector),16),0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,int(hex(sector+12),16)])) #final key
            time.sleep(self.delay)
            writebyte.append(i)
            self.ser.write(writebyte)
            resp = self.ser.read(3)
            print("%s returned %s" %(writebyte,resp))
            del writebyte[-1]
            time.sleep(self.delay)
  
        print("Bruteforce Complete!")
        self.beep()

def main():
    devices = [device.device for device in serial.tools.list_ports.comports()]
    device = None
    if len(devices) == 0:
        print("No devices found, aborting...")
        return

    while device == None:
        print(f"Devices Found - {devices}")
        device = input("Choose a device: ")
        if device not in devices:
            device = None
            print("Invalid Device!")
        else:
            global nfc_reader
            nfc_reader = Reader(device)
            nfc_reader.serial_open()

    #TODO - continue implementing commands
    commands = {
    "beep": nfc_reader.beep,
    "anticollision": nfc_reader.anticollision,
    "manufacture": nfc_reader.manufacture,
    "read": nfc_reader.read_card,
    "write": nfc_reader.write_card
    }

    #TODO - clean up command portion
    print("Enter \"help\" for a list of commands")
    while True:
        command_input = input("NFC> ").lower()
        command_tokens = command_input.split()
        if command_tokens[0] == "exit":
            nfc_reader.serial_close()
            break
        elif command_tokens[0] == None or command_tokens[0] == "" or command_tokens[0] == "help":
            print(f"Available Commands - {[command for command in commands.keys()]}\nUse \"exit\" to close {device} connection and quit")
        elif command_tokens[0] == "read":
            try:
                print(commands[command_tokens[0]](int(command_tokens[1]),int(command_tokens[2])))
            except KeyError:
                print("Invalid Command!")
        elif command_tokens[0] == "write":
            try:
                print(commands[command_tokens[0]](int(command_tokens[1]),int(command_tokens[2]),str(command_tokens[3])))
            except KeyError:
                print("Invalid Command!")
        else:
            try:
                print(commands[command_tokens[0]]())
            except KeyError:
                print("Invalid Command!")

if __name__ == "__main__":
    main()