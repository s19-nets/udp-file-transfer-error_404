#! /usr/bin/env python3

from socket import *
import sys, os, re, time, struct

serverSock = socket(AF_INET,SOCK_DGRAM)
serverSock.settimeout(2)
serverAddr = (('127.0.0.1', 50000))
serverSock.bind(serverAddr)
timeouts = 0
packetID = 1
#temporary eof/end-of-transmission token for clientSock.recv() to stop
eof = ''

print('Waiting for request...')

#Waiting for file request. Checks for timeouts, and
#terminates on 4th.
while 1:
    try:
        (_fileName, clientAddr) = serverSock.recvfrom(100)
        timeouts = 0
        break
    except:
        if timeouts >= 4:
            print('No requests, terminating')
            sys.exit(1)
        print('Timeout, waiting for request...')
        timeouts += 1

fileName = _fileName.decode()

#Makes sure file exists. Terminates if not.
if not os.path.isfile('./' + fileName):
    print('Client requesting non-existant file, terminating.')
    _packet = struct.pack('H98s', 0, eof.encode())
    serverSock.sendto(_packet, clientAddr)
    sys.exit(1)

#Accesses requested file.
print('Client, ' + repr(clientAddr) + ' requesting ' + fileName)
file = open(fileName, 'r')

#Sends packets and waits for acknowledgements until end of document is reached,
#or unless 4 consecutive timeouts occur.
while 1:
    #File contents read and encoded into UTF-8
    fileContents = file.read(98)
    _fileContents = fileContents.encode()

    #PacketID and fileContents converted into bytes object and sent
    _packet = struct.pack('H98s', packetID, _fileContents)
    serverSock.sendto(_packet, clientAddr)

    #Stops and waits for acknowledgement of packet just sent
    #Resends packet if incorrect ID acknowledgement is recieved,
    #or if a timeout occurs.
    while 1:

        #Checks and counts timeouts
        while 1:
            try:
                _ACK = serverSock.recv(2)
                timeouts = 0
                break
            except:
                if timeouts >= 4:
                    print('Client unresponsive, terminating.')
                    sys.exit(1)
                serverSock.sendto(_packet, clientAddr)
                print('Timeout...')
                timeouts += 1

        ACK = struct.unpack('H', _ACK)[0]
        print(str(ACK))
        print(str(packetID))

        #Checks if the proper packet was acknowledged, if not
        #server waits for next acknowledgement
        if ACK == packetID:
            wrongPacket = 0
            break

        #Terminates after the fourth incorrect acknowledgement
        if wrongPacket >= 4:
            print('Network malfunction, terminating.')
            sys.exit(1)
        #Packet is resent so client can acknowledge
        serverSock.sendto(_packet, clientAddr)
        wrongPacket += 1

    #Stops sending packets after end of file is reached.
    #FIX: SERVER NEEDS TO WAIT FOR LAST ACK
    if not fileContents: break
    packetID += 1

serverSock.sendto(eof.encode(), clientAddr)

file.close()

print('File sent')
