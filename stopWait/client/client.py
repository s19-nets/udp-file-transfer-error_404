#! /usr/bin/env python3

from socket import *
import sys, os, re, time

ACK = 'ack'
ACK = ACK.encode()

clientSock = socket(AF_INET,SOCK_DGRAM)
serverAddr = (('127.0.0.1',50000))

fileName = input("Enter the file name in name.extension format.\n")
print('Requesting file: ' + fileName)
requestedFile = open(fileName, 'w')
_fileName= fileName.encode()
clientSock.sendto(_fileName,addr)

while 1:
    _fileContents = clientSock.recv(100)
    clientSock.sendto(ACK, serverAddr)
    fileContents = _fileContents.decode()
    if not fileContents: break
    requestedFile.write(fileContents)

requestedFile.close()
print(fileName + ' recieved.')
