from RTPSocket import RTPSocket
from RTPSocketManager import RTPSocketManager
from RTPPacket import RTPPacket
import sys, select, socket
import threading
import time

def getDataArrayToSend(fileToSend):
    dataArray = []
    while 1:
        chunk = fileToSend.read(128) #128 bit chunks
        dataArray.append(chunk)
        if not chunk:
            break
    return dataArray

def checkForDownloadedDataThread():
    checkForDataThread = threading.Thread(target=checkForDownloadedData)
    checkForDataThread.daemon = True
    checkForDataThread.start()
    print "\nCreated Thread for Checking for Downloads"

def checkForDownloadedData():
    global askForInput
    while 1:
        ipAddressReceived, portNumberReceived,  dataArrayToDownload, dataName = socketPost.recvData()
        if len(dataArrayReceived) != 0 and dataArrayToDownload[0] != "get":
            fileToReceive = open("post_" + dataName, 'wb+')
            for dataChunk in dataArrayToDownload:
                fileToReceive.write(dataChunk)
            fileToReceive.flush()
            fileToReceive.close()
            askForInput = 0

########################################
# CHECK PARAMETERS & make socketManager
########################################

udpPort = -1
maxWindowSize = -1

try:
    if len(sys.argv) != 3:
        print "Please specify a UDP Port and a Maximum Receive Window"
        sys.exit()

    i = 0
    for arg in sys.argv:
        if i == 1:
            udpPort = int(arg)
        if i == 2:
            maxWindowSize = int(arg)
        i = i + 1

    if udpPort == -1 or maxWindowSize == -1:
        print "Invalid Paramteres"
        sys.exit()
except e:
    print "Invalid Paramteres Exception: \n" + str(e.value)
    sys.exit()

########################################

#socket() bind()
socketManager = RTPSocketManager()
socketManager.bindUDP(str(socket.gethostbyname(socket.getfqdn())), udpPort)
socketGet = socketManager.createSocket(99999)
socketPost = socketManager.createSocket(99998)
socketGet.windowSize = maxWindowSize
socketPost.windowSize = maxWindowSize

#thread to check for file download
checkForDownloadedDataThread()

#send responses to get requests
while 1:
    ipAddress, portNumber, dataArrayReceived, fileName = socketGet.recvData()
    if len(dataArrayReceived) != 0 and dataArrayReceived[0] == "get":
        fileToSend = open(fileName, 'rb+')
        dataArray = getDataArrayToSend(fileToSend)
        socketGet.sendData(ipAddress, portNumber, dataArray, fileName)



