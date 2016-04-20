from RTPSocket import RTPSocket
from RTPPacket import RTPPacket
from socket import *
import sys, select
import threading


class RTPSocketManager:

    ####################
    # INITIALIZATION
    ####################
    def __init__(self):
        self.debug = 1
        self.portsAvailable = []
        self.portsTaken = []
        self.sockets = []
        portAssigner = 0
        while len(self.portsAvailable) < 100000:
            self.portsAvailable.append(portAssigner)
            portAssigner += 1
        if self.debug == 1: print 'RTPSocketManager created'
        self.mainSocket = socket(AF_INET, SOCK_DGRAM, 0)

    #8592 or 8591 recommended
    def bindUDP(self, ipAddress, udpPortNumber):
        self.mainSocket.bind((ipAddress, udpPortNumber))
        self.startReceivingPackets()
        if self.debug == 1: print 'RTPSocketManager bound to IP: ' + ipAddress + " Port: " + str(udpPortNumber)

    ####################
    # SOCKET MANAGEMENT
    ####################
    def createSocket(self, portNumber=-1):
        if portNumber == -1:
            "Creates socket assigning it to vitual port"
            portToAssign = -1
            for port in self.portsAvailable:
                if port not in self.portsTaken:
                    portToAssign = port
            self.portsTaken.append(portToAssign)
            #do something with port number
            socketToReturn = RTPSocket(portToAssign, self)
            if portToAssign == -1:
                if self.debug == 1: print "All 100,000 port numbers taken"
            else:
                if self.debug == 1: print "Created virtual socket with port: ", portToAssign
            self.sockets.append(socketToReturn)
            return socketToReturn
        else:
            if portNumber not in self.portsTaken:
                self.portsTaken.append(portNumber)
                socketToReturn = RTPSocket(portNumber, self)
                self.sockets.append(socketToReturn)
                return socketToReturn
            else:
                if self.debug == 1: print "Socket Already Taken"


    def getSocket(self, portNumber):
        for socket in self.sockets:
            if socket.portNumber == portNumber:
                return socket

    ####################
    # RECEIVING
    ####################
    def startReceivingPackets(self):
        receivePacketsThread = threading.Thread(target=self.recvPacket)
        receivePacketsThread.daemon = True
        receivePacketsThread.start()
        if self.debug == 1: print "\nCreated Thread for Receiving Packets"

    def recvPacket(self):
        while 1:
            if self.debug == 1: print "\nWaiting to Receive Packet..."
            message, clientAddress = self.mainSocket.recvfrom(2048)
            packetReceived = RTPPacket("", 0, "", 0, "", 0, 0, "", message)
            if self.debug == 1: print "\nPacket Received from Address " + str(clientAddress) + "\n\tVirtual Port: " + str(packetReceived.destPort) + "\n\tType: " + packetReceived.packetType + "\n\tSequence Number: " + str(packetReceived.seqNum) + "\n\tACK Number: " + str(packetReceived.ackNum) + "\n\tMessage: " + str(packetReceived.data)
            socketOfPacketReceived = self.getSocket(packetReceived.destPort)
            if socketOfPacketReceived is not None:
                socketOfPacketReceived.packetReceived(packetReceived)

    ####################
    # SENDING
    ####################
    def sendPacket(self, packetToSend):
        "sends RTPPacket to where it should go"
        portToSendTo = 8591
        if self.mainSocket.getsockname()[1] == 8591:
            portToSendTo = 8592
        if self.debug == 1: print "\nPacket Sent to IP " + str(packetToSend.destIP) + "\n\tReal Port: " + str(portToSendTo) + "\n\tVirtual Port: " + str(packetToSend.destPort) + "\n\tType: " + packetToSend.packetType + "\n\tSequence Number: " + str(packetToSend.seqNum) + "\n\tACK Number: " + str(packetToSend.ackNum) + "\n\tMessage: " + str(packetToSend.data)
        self.mainSocket.sendto(packetToSend.getFileToSend(),(packetToSend.destIP, portToSendTo))
        return



