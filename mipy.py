import serial
from serial.tools import list_ports
import time
import re

#TODO - fix pyserial doing ASCII over pure hex data in returns (possible translator function??)
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
        self.ser.timeout = 0.25
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
        resp = self.ser.readall()
        self.beep()
        return resp[-5:-1]

    def read_card(self,sector,block):
        self.card_check()
        self.ser.write(self.nfc_protocol["starter"])
        self.ser.read(8)
        time.sleep(self.delay)
        self.ser.write(bytearray([0x0A,0x05,int(hex(sector),16),0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,int(hex(sector+12),16)])) #final bytekey
        self.ser.read(3)
        time.sleep(self.delay)
        self.ser.write(bytearray([0x03,0x06,int(hex((4*sector)+block),16),int(hex(9+(4*sector)+block),16)])) #read data
        resp = self.ser.readall()
        self.beep()
        return resp[-17:-1]

    def write_card(self,sector,block,data=b""):
        writebyte = bytearray([0x13,0x07,int(hex((4*sector)+block),16)])
   
        #card data handler
        if len(data) > 16:
            return "Data longer than 16 char/hex!"

        while len(data) < 16:
            data += b"\x00"
        
        #checksum calc
        checksum_bit = 0x1A
        checksum_bit += block
        checksum_bit += sector * 4
        for b in data:
            checksum_bit += b

        while checksum_bit > 0xFF:
            checksum_bit -= 0x100
        
        #append data
        for bit in data:
            writebyte.append(bit)

        writebyte.append(checksum_bit)

        self.card_check()
        self.ser.write(self.nfc_protocol["starter"])
        #self.ser.read(8)
        time.sleep(self.delay)
        self.ser.write(bytearray([0x0A,0x05,int(hex(sector),16),0x03,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,int(hex(sector+12),16)])) #final key
        time.sleep(self.delay)
        self.ser.write(writebyte)
        time.sleep(self.delay)
        self.beep()
        return "Write Complete!"

    def dump(self):
        filename = f"{self.anticollision()} - {time.asctime()}.txt".replace(":","-")
        filename_final = re.sub("\\\\x|b'|'","",filename)
        dump_file = open(filename_final,"w")
        time.sleep(self.delay)
        for i in range(16):
            dump_file.write(f"Sector {i}\n")
            for j in range(4):
                data = self.read_card(i,j)
                dump_file.write(f"{data}\n")
                print(f"Progress: {j+(i*4)+1}/64")

        dump_file.close()
        return "Dump Complete!"



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
    "write": nfc_reader.write_card,
    "format": nfc_reader.write_card
    }

    #TODO - clean up command portion heavily
    print("Enter \"help\" for a list of commands")
    while True:
        nfc_reader.ser.reset_input_buffer()
        nfc_reader.ser.reset_output_buffer()
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
            except IndexError:
                print("Incomplete command!")
        elif command_tokens[0] == "write":
            try:
                print(commands[command_tokens[0]](int(command_tokens[1]),int(command_tokens[2]),bytes(command_tokens[3].encode('utf-8'))))
            except KeyError:
                print("Invalid Command!")
            except IndexError:
                print("Incomplete command!")
        elif command_tokens[0] == "format":
            try:
                print(commands[command_tokens[0]](int(command_tokens[1]),int(command_tokens[2])))
            except KeyError:
                print("Invalid Command!")
            except IndexError:
                print("Incomplete command!")
        else:
            try:
                print(commands[command_tokens[0]]())
            except KeyError:
                print("Invalid Command!")

if __name__ == "__main__":
    main()