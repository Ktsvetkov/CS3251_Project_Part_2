from RTPSocket import RTPSocket
from RTPSocketManager import RTPSocketManager
from RTPPacket import RTPPacket
import sys, select


########################################
# CHECK PARAMETERS & make socketManager
########################################
if len(sys.argv) < 2:
    print "Please specify client or server"
    sys.exit()

typeOfGUI = ""
i = 0
for arg in sys.argv:
    if i == 1:
        typeOfGUI = arg
    i = i + 1

socketManager = RTPSocketManager()

if typeOfGUI == "client":
    socketManager.bindClient()
elif typeOfGUI == "server":
    socketManager.bindServer()
else:
    print "Please specify client or server"
    sys.exit()

########################################

socket = socketManager.createSocket()

dataToSend = []
i = 0
while i < 100:
    dataToSend.append(str(i))
    i += 1

if typeOfGUI == "client":
    socket.sendData(dataToSend, "127.0.0.1", 99999)

while 1:
    i += 1