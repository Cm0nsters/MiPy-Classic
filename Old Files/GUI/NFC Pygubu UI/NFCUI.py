#Imports
import tkinter as tk
from tkinter import messagebox
import pygubu
import NFCGuiBackend
import CardSectorData

#Application Class
class Application:
    def __init__(self, master):

        #1: Create builder
        self.builder = builder = pygubu.Builder()

        #2: Load ui file
        builder.add_from_file('NFC.ui')

        #3: Create widget using master as parent
        self.mainwindow = builder.get_object('mainwindow', master)

        # Connect method callbacks
        builder.connect_callbacks(self)

    # define the method callbacks
    def on_button1_clicked(self):
        messagebox.showinfo('Message', 'You clicked Button 1')
    
    #Callback Functions
    def beepToggleUpdate(self):
        toggle = self.builder.get_variable('beeptoggle')
        toggle = toggle.get()
        print(toggle)
        if toggle == 0:
            print("off")
        else:
            print("on")

    def hexRead(self):
        NFCGuiBackend.manufacture()
        messagebox.showinfo('Hex Read', 'Manufacture Data (S0B0) was read!\nData:\n%s' %(NFCGuiBackend.data))

#UI run loop
if __name__ == '__main__':
    root = tk.Tk()
    root.title("NFCPy Read/Write")
    app = Application(root)
    root.mainloop()
