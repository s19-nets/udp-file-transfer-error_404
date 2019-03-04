#! /usr/bin/env python3

from socket import *
import sys, os, re, time, struct

clientSock = socket(AF_INET,SOCK_DGRAM)
clientSock.settimeout(2)
serverAddr = (('127.0.0.1',50000))

#fileName = input("Enter the file name in name.extension format.\n")
fileName = 'test.txt'
print('Requesting file: ' + fileName)
requestedFile = open(fileName, 'w')
_fileName= fileName.encode()
clientSock.sendto(_fileName, serverAddr)
expectedID = 1
wrongPacket = 0


while 1:
    #Checks for timeouts
    try:
        _packet = clientSock.recv(100)
    except:
        print('Server unresponsive, terminating.')
        sys.exit(1)

    #Stops waiting for packets when empty string is recieved (EOF signal)
    if not _packet: break

    #TODO: consider trying to remove padding in last packet
    (packetID, _fileContents) = struct.unpack('H98s', _packet)

    #Stops and waits until expected packet is recieved.
    #Terminates after four incorrect packets arrive, assumes network
    #is unstable
    while packetID != expectedID:
        #Checks for timeouts
        try:
            _packet = clientSock.recv(100)
        except:
            print('Server unresponsive, terminating.')
        (packetID, _fileContents) = struct.unpack('H98s', _packet)
        wrongPacket += 1
        if wrongPacket >=4:
            print('Network malfunction, terminating.')
            sys.exit(1)
            
    #Decode and write text to file
    fileContents = _fileContents.decode()
    print(fileContents)
    requestedFile.write(str(fileContents))

    #Sends acknowledgement containing ID of recieved packet back to server
    ACK = struct.pack('H', packetID)
    clientSock.sendto(ACK, serverAddr)
    expectedID += 1

requestedFile.close()
print(fileName + ' recieved.')
