#Start making help section stuff
def helpCommand(command):
    if command == "":
        print("AVAILABLE COMMANDS:")
        print(helpCommandData.keys())
    elif command in helpCommandData:
        print(helpCommandData[command])
    else:
        print("Sorry, but this command doesn't exist! Use 'help' to see the available commands")        

helpCommandData = {
    "help": "Shows help data",
    "setdevice": "Use to change serial port",
    "devicename": "Prints current serial device",
    "beeptoggle": "Toggles speaker of NFC pad",
    "beep": "Beeps NFC device",
    "changekey": "NOT IMPLEMENTED",
    "anticollision": "Prints anticollision",
    "manufacture": "Prints manufacture data of NFC Card",
    "sectorread": "Use to read data on card",
    "sectorwrite": "Use to write data to . Leave 'Data:' blank to clear data from block(BETA)"
}