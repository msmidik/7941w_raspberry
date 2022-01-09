#!/usr/bin/env python3
#7941w rfid card reader/writer on raspberry pi

import serial
import time
import sys

rfidSerial =  serial.Serial('/dev/serial0', baudrate=115200, timeout=1.0)
time.sleep(0.5)

def main() :
    if len(sys.argv) == 1 :
        printHelpAndExit()
    if sys.argv[1] == 'r' :
        readLoop()
    elif sys.argv[1] == 'rs' :
        readSector(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == 'ra' :
        readAll(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'wu' :
        writeUid(sys.argv[2])
    elif sys.argv[1] == 'wi' :
        writeId(sys.argv[2])
    elif sys.argv[1] == "ws" :
        writeSector(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif sys.argv[1] == 'm' :
        modifyPassword(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else :
        printHelpAndExit()

def printHelpAndExit() :
    print("Arguments:")
    print(" r \t read ID and UID in loop")
    print(" rs <sector> <block> <group> <password> \t read specified sector, sector and block are 1 byte, group password 0a or 0b, password 6 bytes ")
    print(" ra <group> <password> \t read all sectors (M1-1K card), group password 0A or 0B, password 6 bytes")
    print(" wu <uid> \t write UID (4 bytes) use default password ffffffffffff")
    print(" wi <id> \t write id (T5577 number)")
    print(" ws <sector> <block> <group> <password> <data>  \t write specified sector, sector and block are 1 byte, group password 0a or 0b, password 6 bytes, data 16 bytes")
    print(" m <sector> <group> <old_password> <new_password> \t modify password of group A or B, password 6 bytes")
    sys.exit()

def readLoop() :
    while True:
        processRead(0x10, "UID")
        time.sleep(0.5)
        processRead(0x15, "ID")
        time.sleep(0.5)
        
def processRead (cmd, type) :
    processing = False
    sendCommand(0, cmd, None)
    if rfidSerial.inWaiting() == 0 :
        processing = True
    time.sleep(0.1)
    resp = rfidSerial.read(rfidSerial.inWaiting())
    result = parseResponse(resp)
    if result is None and not(processing):
        print('.', end='', flush=True)
    elif result is None and processing:
        print(type[0], end='', flush=True)
    else:
        print()
        print("(" + type + ") " + result)

def readSector(sector, block, group, password) :
    data = bytes.fromhex(sector + block + group + password)
    sendAndPrint(0, 0x12, data)

def readAll(group, password) :
    data = bytes.fromhex(group + password)
    sendAndPrint(0, 0x17, data)
    
def writeUid(uid) :
    data = bytes.fromhex(uid)
    sendAndPrint(0, 0x11, data)
    
def writeId(id) :
    data = bytes.fromhex(id)
    sendAndPrint(0, 0x16, data)
    
def writeSector(sector, block, group, password, write_data) :
    data = bytes.fromhex(sector + block + group + password + write_data)
    sendAndPrint(0, 0x13, data)
    
def modifyPassword(sector, group, old, new) :
    data = bytes.fromhex(sector + group + old + new)
    sendAndPrint(0, 0x14, data)

def sendCommand(address, cmd, data) :
    if data is None :
        dataLength = 0
    else:
        dataLength = len(data)
    cmdLength = 6 + dataLength
    command = bytearray(cmdLength)
    command[0] = 0xAB
    command[1] = 0xBA
    command[2] = address
    command[3] = cmd
    command[4] = dataLength
    cmdIndex = 5
     
    for i in range(dataLength):
        command[cmdIndex+i] = data[i]
    
    command[cmdLength-1] = xorCheck(command, 3, cmdLength-2)
    rfidSerial.write(command)
    rfidSerial.flush()
    #print("Sent: " + formatHex(command))

def sendAndPrint(address, cmd, data) :
    sendCommand(address, cmd, data)
    time.sleep(0.5)
    resp = rfidSerial.read(rfidSerial.inWaiting())
    result = parseResponse(resp)
    if result is None :
        print("Operation failed")
    else:
        print(result)

def xorCheck(array, start, end) :
    result = 0
    for i in range(start, end+1):
        result = result ^ array[i]
    return result;

def parseResponse(resp) :
    respLength = len(resp)
    if respLength == 0 :
        return "No response"
    if xorCheck(resp, 3, respLength-2) != resp[respLength-1] :
        return "XOR check failed: " + formatHex(resp)
    if resp[0] != 0xCD or resp[1] != 0xDC :
        return "Invalid header: " + formatHex(resp)
    if resp[3] == 0x81 :
        dataLength = resp[4]
        data = resp[5:5+dataLength]
        return "Operation succeded: " + formatHex(data)
    elif resp[3] == 0x80 :
        return None
    else:
        return "Unexpected return value: " + formatHex(resp)

def formatHex(str) :
    return " ".join("{:02x}".format(c) for c in str)

main()
