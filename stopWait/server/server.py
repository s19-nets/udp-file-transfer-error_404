#! /usr/bin/env python3

from socket import *
import sys, os, re, time, struct

serverSock = socket(AF_INET,SOCK_DGRAM)
serverAddr = (('127.0.0.1',50000))
serverSock.bind(serverAddr)
print('Waiting for request...')

(_fileName, clientAddr) = serverSock.recvfrom(2048)
fileName = _fileName.decode()
print('Client, ' + repr(clientAddr) + ' requesting ' + fileName)

file = open(fileName, 'r')

timeouts = 0
packetID = 1

while 1:
    #File contents read and encoded into UTF-8
    fileContents = file.read(98)
    _fileContents = fileContents.encode()

    #PacketID and fileContents converted into bytes object and sent
    _packet = struct.pack('H98s', packetID, _fileContents)
    serverSock.sendto(_packet, clientAddr)

    #Stops and waits for acknowledgement of packet just sent
    #Resends packet if incorrect ID acknowledgement is recieved
    while 1:
        _ACK = serverSock.recv(2)
        ACK = struct.unpack('H', _ACK)[0]
        print(str(ACK))
        print(str(packetID))
        if ACK == packetID: break
        serverSock.sendto(_packet, clientAddr)

    if not fileContents: break
    packetID += 1

#temporary eof token for recv() to stop
eof = ''
serverSock.sendto(eof.encode(), clientAddr)

file.close()

print('File sent')
