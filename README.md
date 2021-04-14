# MiPy-Classic
## What is *MiPy-Classic*?
MiPy is a tool designed for interacting with Mifare Classic 1K NFC chips using the M302 Reader/Writer
## Status and Functionality
MiPy is still very much a Work-In-Progress, but already contains a competent set of tools to achieve basic functionality

**NOTES:**
 - Items marked WIP are still being developed
 - More features may be added in the future and will be documented below

**Full Feature List and Status**
```
Card Detection - Final
CLI - WIP/Final (Still adding features, but functionable)
GUI - Not Implemented (WIP/Alpha in previous V2 version)
Anticollision - Final
Read manufacture data - Final (Functions with default key only)
Read card - Final
Write card - WIP/Beta (Currently only supports bruteforcing the CRC)
Change key - Not Implemented
Change key type used - Not Implemented
Change key of card - Not Implemented
Value Blocks - Not Implemented
NDEF Formatting - Not Implemented
Module Support - WIP/Beta
```
## TO-DO
MiPy supports CLI only, but a pre-included GUI is planned. Module support is also currently a WIP, but currently has basic functionality *(see NFC-Extenstion-Demo.py)*
```
TO-DO:
 - Continue to reverse engineer write CRC
 - Study NDEF format on Mifare Classic platform
 - Develop GUI
 - Continue Development of module support
```
