#! /usr/bin/env python3

from socket import *
from select import select
import sys, os, re, time, struct

clientSock = socket(AF_INET,SOCK_DGRAM)
clientSock.setblocking(False)
serverAddr = (('127.0.0.1',50000))
expectedID = 1
timeout = 20

#fileName = input("Enter the file name in name.extension format.\n")
fileName = 'test.txt'
print('Requesting file: ' + fileName)
requestedFile = open(fileName, 'w')
_fileName= fileName.encode()
clientSock.sendto(_fileName, serverAddr)


def processPacket():
    global expectedID

    _packet = clientSock.recv(100)
    if not _packet: closeFile()

    #TODO: consider trying to remove padding in last packet
    (packetID, _fileContents) = struct.unpack('H98s', _packet)

    print(str(expectedID))
    print(str(packetID))

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
    print('client boop')

def closeFile():
    requestedFile.close()
    print(fileName + ' recieved.')
    sys.exit(1)


readSockFunc = {}
writeSockFunc = {}
errorSockFunc = {}

readSockFunc[clientSock] = processPacket

while 1:
    readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()),
                                                list(errorSockFunc.keys()),
                                                timeout)

    if not readRdySet and not writeRdySet and not errorRdySet:
        print('Server unresponsive. Request terminated.')
        sys.exit(1)

    for sock in readRdySet:
        print('Packet recieved')
        readSockFunc[sock]()
