from RTPPacket import RTPPacket
from socket import *
import sys, select, socket
import time
import threading



class RTPSocket:

    def __init__(self, portNumber, socketManager):
        ##### packet loss
        self.connectTimer = threading.Timer(.2, self.resendConnect)
        self.acceptTimer = threading.Timer(.2, self.resendAccept)
        self.dataTimer = threading.Timer(.2, self.resendData)
        self.closeReceiverTimer = threading.Timer(.2, self.resendCloseReceiver)
        #####

        self.portNumber = portNumber
        self.socketManager = socketManager
        self.srcIP = str(socket.gethostbyname(socket.getfqdn()))

        self.hasData = 0
        self.isSending = 0
        self.isReceiving = 0

        self.readyForGet = 0
        self.fileToGet = ""

        self.incomingConnectionIP = ""
        self.incomingConnectionPort = 0
        self.outgoingConnectionIP = ""
        self.outgoingConnectionPort = 0

        self.dataToSend = []
        ##### Window Sender
        self.dataToSendConfirmation = []
        #####
        self.dataToSendName = ""
        self.dataReceived = []
        self.dataReceivedName = ""

        self.windowSize = 1
        self.windowPosition = 0

    def packetReceived(self, packetReceived):

        #Receiving Methods
        if packetReceived.packetType == "connect":
            self.isReceiving = 1
            self.incomingConnectionIP = packetReceived.srcIP
            self.incomingConnectionPort = packetReceived.srcPort
            packetToSend = RTPPacket(packetReceived.srcIP, packetReceived.srcPort, self.srcIP, packetReceived.destPort, "accept", packetReceived.seqNum, packetReceived.ackNum + 1, "")

            self.socketManager.sendPacket(packetToSend)
            ##### packet loss
            self.acceptTimer.cancel()
            self.acceptTimer = threading.Timer(.2, self.resendAccept)
            self.acceptTimer.start()
            #####

        elif packetReceived.packetType == "data":
            ##### packet loss
            if packetReceived.seqNum == 1:
                self.acceptTimer.cancel()
            #####
            ##### Window Receiver
            if self.shouldReceiverWindowMove():
                self.extendReceiverWindow()
            self.addReceiverData(packetReceived.seqNum-1, packetReceived.data)
            #####
            packetToSend = RTPPacket(packetReceived.srcIP, packetReceived.srcPort, self.srcIP, packetReceived.destPort, "ack", packetReceived.seqNum, packetReceived.ackNum + 1, "")

            self.socketManager.sendPacket(packetToSend)

        elif packetReceived.packetType == "closereceiver":
            ##### Window Receiver
            self.dataReceived = self.trimReceiverData(self.dataReceived)
            self.windowPosition = 0
            # print "\nDataReceived Length: " + str(len(self.dataReceived))
            # print "\n" + str(self.dataReceived)
            #####
            self.isReceiving = 0
            self.hasData = 1
            self.dataReceivedName = packetReceived.data
            packetToSend = RTPPacket(packetReceived.srcIP, packetReceived.srcPort, self.srcIP, packetReceived.destPort, "closesender", 0, 0, "")
            self.socketManager.sendPacket(packetToSend)


        #Sender Methods
        elif packetReceived.packetType == "accept":
            ##### packet loss
            self.connectTimer.cancel()
            #####
            ##### Window Sender
            self.makeSureDataToSendConfirmNotZero()
            self.sendWindowOfPackets()
            #####
            ##### packet loss
            self.dataTimer.cancel()
            self.dataTimer = threading.Timer(.2, self.resendData)
            self.dataTimer.start()
            #####

        elif packetReceived.packetType == "ack":
            ##### Window Sender
            self.confirmSenderData(packetReceived.ackNum-2)
            if self.shouldSenderWindowMove():
                self.extendSenderWindow()
                self.sendWindowOfPackets()
                ##### packet loss
                self.dataTimer.cancel()
                self.dataTimer = threading.Timer(.2, self.resendData)
                self.dataTimer.start()
                #####
            #####
            if self.actualSenderWindowLength(self.dataToSendConfirmation) >= len(self.dataToSend):
                ##### packet loss
                self.dataTimer.cancel()
                #####
                packetToSend = RTPPacket(packetReceived.srcIP, packetReceived.srcPort, self.srcIP, packetReceived.destPort, "closereceiver", 0, 0, self.dataToSendName)
                self.socketManager.sendPacket(packetToSend)
                ##### packet loss
                self.closeReceiverTimer.cancel()
                self.closeReceiverTimer = threading.Timer(.2, self.resendCloseReceiver)
                self.closeReceiverTimer.start()
                #####

        elif packetReceived.packetType == "closesender":
            ##### packet loss
            self.closeReceiverTimer.cancel()
            #####
            ##### Window Sender
            self.dataToSendConfirmation = []
            self.windowPosition = 0
            #####
            self.isSending = 0
            self.dataToSend = []
            self.dataToSendName = ""
            self.outgoingConnectionIP = ""
            self.outgoingConnectionPort = 0


    def sendData(self, destIP, destPort, dataToSend, dataToSendName=""):
        self.readyForGet = 0
        self.fileToGet = ""
        self.isSending = 1
        self.outgoingConnectionIP = destIP
        self.outgoingConnectionPort = destPort
        self.dataToSend = dataToSend
        self.dataToSendName = dataToSendName
        packetToSend = RTPPacket(destIP, destPort, self.srcIP, self.portNumber, "connect", 0, 0, "")
        self.socketManager.sendPacket(packetToSend)
        ##### packet loss
        self.connectTimer.cancel()
        self.connectTimer = threading.Timer(.2, self.resendConnect)
        self.connectTimer.start()
        #####

    def recvData(self):
        while 1:
            for socketUsed in self.socketManager.sockets:
                if socketUsed.hasData == 1 and socketUsed.portNumber == self.portNumber:
                    incomingIP = socketUsed.incomingConnectionIP
                    incomingPort = socketUsed.incomingConnectionPort
                    dataToReturn = socketUsed.dataReceived
                    dataDescription = socketUsed.dataReceivedName
                    socketUsed.dataReceived = []
                    socketUsed.hasData = 0
                    socketUsed.dataReceivedName = ""
                    socketUsed.incomingConnectionIP = ""
                    socketUsed.incomingConnectionPort = 0
                    return incomingIP, incomingPort, dataToReturn, dataDescription
            time.sleep(1)

########################################
# Packet Loss Methods
########################################
    def resendConnect(self):
        packetToSend = RTPPacket(self.outgoingConnectionIP, self.outgoingConnectionPort, self.srcIP, self.portNumber, "connect", 0, 0, "")
        self.socketManager.sendPacket(packetToSend)
        self.connectTimer = threading.Timer(.2, self.resendConnect)
        self.connectTimer.start()

    def resendAccept(self):
        packetToSend = RTPPacket(self.outgoingConnectionIP, self.outgoingConnectionPort, self.srcIP, self.portNumber, "accept", 0, 1, "")
        self.socketManager.sendPacket(packetToSend)
        self.acceptTimer = threading.Timer(.2, self.resendAccept)
        self.acceptTimer.start()

    def resendData(self):
        self.sendWindowOfPackets()
        self.dataTimer = threading.Timer(.2, self.resendData)
        self.dataTimer.start()
        print "\n Current Data Confirmation: " + str(self.dataToSendConfirmation) + "\n"

    def resendCloseReceiver(self):
        packetToSend = RTPPacket(self.outgoingConnectionIP, self.outgoingConnectionPort, self.srcIP, self.portNumber, "closereceiver", 0, 0, self.dataToSendName)
        self.socketManager.sendPacket(packetToSend)
        self.closeReceiverTimer = threading.Timer(.2, self.resendCloseReceiver)
        self.closeReceiverTimer.start()


########################################
# Receiver Window Control Methods
########################################
    def addReceiverData(self, index, dataToAdd):
        if index >= self.windowPosition and index < self.windowPosition + self.windowSize:
            if self.dataReceived[index] == "":
                self.dataReceived[index] = dataToAdd

    def shouldReceiverWindowMove(self):
        if len(self.dataReceived) == 0:
            return True
        for i in range(self.windowSize):
            if self.dataReceived[self.windowPosition+i] == "":
                return False
        return True

    def extendReceiverWindow(self):
        if len(self.dataReceived) == 0:
            for i in range(self.windowSize):
                self.dataReceived.append("")
        else:
            self.windowPosition = self.windowPosition + self.windowSize
            for i in range(self.windowSize):
                self.dataReceived.append("")

    def trimReceiverData(self, arrayToTrim):
        trimIterator = len(arrayToTrim) - 1
        while trimIterator >= 0 and arrayToTrim[trimIterator] == "":
            arrayToTrim.pop()
            trimIterator -= 1
        return arrayToTrim

########################################
# Receiver Window Control Methods
########################################

    def sendWindowOfPackets(self):
        print "Sending window of packets"
        mostRecentSeq = self.windowPosition + 1
        mostRecentAck = mostRecentSeq
        print "Most Recent SEQ: " + str(mostRecentSeq)
        print "Most Recent ACK: " + str(mostRecentAck)
        for i in range(self.windowSize):
            if self.windowPosition + i < len(self.dataToSend):
                dataChunkToSend = self.dataToSend[self.windowPosition + i]
                packetToSend = RTPPacket(self.outgoingConnectionIP, self.outgoingConnectionPort, self.srcIP, self.portNumber, "data", mostRecentSeq + i, mostRecentAck + i, dataChunkToSend)
                self.socketManager.sendPacket(packetToSend)

    def makeSureDataToSendConfirmNotZero(self):
        if len(self.dataToSendConfirmation) == 0:
            for i in range(self.windowSize):
                self.dataToSendConfirmation.append("")
            print "Initial 10 elements: " + str(self.dataToSendConfirmation)

    def confirmSenderData(self, index):
        print "Element attempted confirm index: " + str(index)
        if index >= self.windowPosition and index < self.windowPosition + self.windowSize:
            if self.dataToSendConfirmation[index] == "":
                self.dataToSendConfirmation[index] = "sent"
                print "Element confirmed at index: " + str(index) + " Now is: " + str(self.dataToSendConfirmation)

    def shouldSenderWindowMove(self):
        print "IF STATEMENT CALLED \n\n"
        for i in range(self.windowSize):
            print "Element " + str(i) + ": " + self.dataToSendConfirmation[self.windowPosition+i] + "\n"
            if self.dataToSendConfirmation[self.windowPosition+i] == "":
                return False
        return True

    def extendSenderWindow(self):
        self.windowPosition = self.windowPosition + self.windowSize
        for i in range(self.windowSize):
            self.dataToSendConfirmation.append("")
        print "Extended by method 2: " + str(self.dataToSendConfirmation)
        print "Window Size: " + str(self.windowSize)
        print "Window Position: " + str(self.windowPosition)

    def actualSenderWindowLength(self, arrayToMeasure):
        i = 0
        for elementToMeasure in arrayToMeasure:
            if elementToMeasure == "sent":
                i += 1
        return i



