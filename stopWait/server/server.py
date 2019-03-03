#! /usr/bin/env python3

from socket import *
import sys, os, re, time

eofToken = ''
eofToken = eofToken.encode()

serverSock = socket(AF_INET,SOCK_DGRAM)
serverAddr = (('127.0.0.1',50000))
serverSock.bind(serverAddr)
print('Waiting for request...')

(_fileName, clientAddr) = serverSock.recvfrom(2048)
fileName = _fileName.decode()
print('Client, ' + repr(clientAddr) + ' requesting ' + fileName)

file = open(fileName, 'r')

while 1:
    fileContents = file.read(100)
    _fileContents = fileContents.encode()
    serverSock.sendto(_fileContents, clientAddr)
    if not fileContents: break
file.close()

print('File sent')
