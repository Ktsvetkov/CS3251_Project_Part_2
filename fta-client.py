from RTPSocket import RTPSocket
from RTPSocketManager import RTPSocketManager
from RTPPacket import RTPPacket
import sys, select, socket
import threading
import time
from termios import tcflush, TCIFLUSH


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
        ipAddressReceived, portNumberReceived,  dataArrayToDownload, dataName = socketGet.recvData()
        fileToReceive = open("get_" + dataName, 'wb+')
        for dataChunk in dataArrayToDownload:
            fileToReceive.write(dataChunk)
        fileToReceive.flush()
        fileToReceive.close()
        askForInput = 0

########################################
# CHECK PARAMETERS & make socketManager
########################################

ipAddress = ""
udpPort = -1
maxWindowSize = -1
askForInput = 0


try:
    if len(sys.argv) != 3:
        print "Please specify a UDP Port and a Maximum Receive Window"
        sys.exit()

    i = 0
    for arg in sys.argv:
        if i == 1:
            addresses = str(arg).split(':')
            ipAddress = addresses[0]
            udpPort = addresses[1]
        if i == 2:
            maxWindowSize = int(arg)
        i = i + 1

    if udpPort == -1 or maxWindowSize == -1 or ipAddress == "":
        print "Invalid Paramteres"
        sys.exit()
except e:
    print "Invalid Paramteres Exception: \n" + str(e.value)
    sys.exit()

########################################

#socket() bind()
socketManager = RTPSocketManager()
socketManager.bindUDP(str(socket.gethostbyname(socket.getfqdn())), 8591)
socketGet = socketManager.createSocket(99999)
socketPost = socketManager.createSocket(99998)
socketGet.windowSize = maxWindowSize
socketPost.windowSize = maxWindowSize

#thread to check for file download
checkForDownloadedDataThread()

#send get request or file based off of commands
while 1:
    if askForInput == 0:
        askForInput = 1

        tcflush(sys.stdin, TCIFLUSH)
        action = raw_input("\nPlease enter command: \n")
        actionArray = action.split(" ")
        if actionArray[0] == "disconnect":
            break
        elif actionArray[0] == "get":
            socketGet.sendData(ipAddress, 99999, ["get"], actionArray[1])
        # elif actionArray[0] == "post":
        #     fileToSend = open(actionArray[1], 'rb+')
        #     dataArray = getDataArrayToSend(fileToSend)
        #     socketPost.sendData(ipAddress, 99998, dataArray, actionArray[1])
        elif actionArray[0] == "get-post":
            fileToSend = open(actionArray[2], 'rb+')
            dataArray = getDataArrayToSend(fileToSend)
            socketPost.sendData(ipAddress, 99998, dataArray, actionArray[2])
            time.sleep(1)
            socketGet.sendData(ipAddress, 99999, ["get"], actionArray[1])
    else:
        time.sleep(1)





