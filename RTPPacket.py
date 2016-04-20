from socket import *
import sys, select, pickle



class RTPPacket:

    def __init__(self, destIP="", destPort=0, srcIP="", srcPort=0, packetType="", seqNum=0, ackNum=0, dataToSend="", fileReceived=""): #, windowSize, checkSum, type, padding):
        if fileReceived is "":
            self.destIP = destIP
            self.destPort = destPort
            self.srcIP = srcIP
            self.srcPort = srcPort
            self.packetType = packetType
            self.seqNum = seqNum
            self.ackNum = ackNum
            self.data = dataToSend
        else:
            "Should construct packet variable from bit stream version"
            packetReceived = pickle.loads(fileReceived)
            self.destIP = packetReceived.destIP
            self.destPort = packetReceived.destPort
            self.srcIP = packetReceived.srcIP
            self.srcPort = packetReceived.srcPort
            self.packetType = packetReceived.packetType
            self.seqNum = packetReceived.seqNum
            self.ackNum = packetReceived.ackNum
            self.data = packetReceived.data

    def getFileToSend(self):
        "Should return bit stream version of all attributes"
        return pickle.dumps(self)