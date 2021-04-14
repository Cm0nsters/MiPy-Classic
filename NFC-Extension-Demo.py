import mipy

#Demo program for implementing module support

device = mipy.Reader('COM8')
print(repr(device))
print(device)
device.serial_open()
print(device.manufacture())
device.serial_close()