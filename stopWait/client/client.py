#! /usr/bin/env python3

from socket import *
import sys, os, re, time, struct

clientSock = socket(AF_INET,SOCK_DGRAM)
serverAddr = (('127.0.0.1',50000))

#fileName = input("Enter the file name in name.extension format.\n")
fileName = 'test.txt'
print('Requesting file: ' + fileName)
requestedFile = open(fileName, 'w')
_fileName= fileName.encode()
clientSock.sendto(_fileName, serverAddr)
expectedID = 1

while 1:
    _packet = clientSock.recv(100)
    if not _packet: break

    #TODO: consider trying to remove padding in last packet
    (packetID, _fileContents) = struct.unpack('H98s', _packet)

    #Stops and waits until expected packet is recieved
    while packetID != expectedID:
        _packet = clientSock.recv(100)
        (packetID, _fileContents) = struct.unpack('H98s', _packet)

    fileContents = _fileContents.decode()
    print(fileContents)
    requestedFile.write(str(fileContents))

    #Sends acknowledgement containing ID of recieved packet back to server
    ACK = struct.pack('H', packetID)
    clientSock.sendto(ACK, serverAddr)
    expectedID += 1

requestedFile.close()
print(fileName + ' recieved.')
