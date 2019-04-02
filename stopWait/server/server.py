#! /usr/bin/env python3

from socket import *
from select import select
import sys, os, re, time, struct

serverSock = socket(AF_INET,SOCK_DGRAM)
serverAddr = (('127.0.0.1',50000))
serverSock.bind(serverAddr)
print('Waiting for request...')
clientAddr = ''
fileName = ''
file = 0
timeout = 3
timeouts = 0
packetID = 1
_packet = ''

def openFile(sock):
    global clientAddr
    global file
    global fileName

    (_fileName, clientAddr) = sock.recvfrom(2048)
    fileName = _fileName.decode()
    print('Client, ' + repr(clientAddr) + ' requesting ' + repr(fileName))
    file = open(fileName, 'r')

def sendNextPacket(sock):
    global packetID
    global file
    global clientAddr

    #File contents read and encoded into UTF-8
    fileContents = file.read(98)
    if not fileContents:
        #temporary
        eof = ''
        sock.sendto(eof.encode(), clientAddr)
        file.close()
        print('File sent')
        sys.exit(1)
    _fileContents = fileContents.encode()

    #PacketID and fileContents converted into bytes object and sent to client
    _packet = struct.pack('H98s', packetID, _fileContents)
    sock.sendto(_packet, clientAddr)

    #Stops and waits for acknowledgement of packet just sent
    #Resends packet if incorrect ID acknowledgement is recieved
    print('boopserver')


def checkAck(sock):
    global packetID
    global _packet
    global clientAddr

    _ACK = sock.recv(2)
    ACK = struct.unpack('H', _ACK)[0]
    print(str(ACK))
    print(str(packetID))
    if ACK == packetID:
        packetID += 1
        return True
    return False

def resendPacket(sock):
    global _packet
    global clientAddr
    sock.sendto(_packet, clientAddr)


readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}

readSockFunc[serverSock] = sendNextPacket

while 1:
    print('boopwhile')
    readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()),
                                                list(errorSockFunc.keys()),
                                                timeout)

    if not readRdySet and not writeRdySet and not errorRdySet:
        print('timeout...')
        timeouts += 1
        if timeouts >= 4:
            print('Client unresponsive, terminating')
            if fileName: file.close()
            sys.exit(1)

    for sock in readRdySet:
        print('boopfor')
        if fileName == '':
            openFile(sock)
            sendNextPacket(sock)
        elif checkAck(sock) == True:
            sendNextPacket(sock)
        else:
            resendPacket(sock)
