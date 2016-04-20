from Tkinter import *
import ttk
import Tkinter
import tkFileDialog as filedialog
import socket
from RTPSocketManager import RTPSocketManager
from RTPSocket import RTPSocket
from RTPPacket import RTPPacket

########################################
# BUTTON FUNCTIONS
########################################

def chooseFile():
    fileLocationPath.set(filedialog.askopenfilename())

def sendFile():
    fileToSend = open(fileLocationPath.get(), 'r+')
    dataArray = getDataArrayToSend(fileToSend)
    fileToSend.close()
    socketToUse = rtpSocketManager.getSocket(int(portToUse.get()))
    if socketToUse is None:
        if portToUse.get() != "":
            socketToUse = rtpSocketManager.createSocket(int(portToUse.get()))
        else:
            socketToUse = rtpSocketManager.createSocket()
        portsUsedStringVar.set(rtpSocketManager.getPortsUsedString())
    socketToUse.sendData(dataArray, ipToSendTo.get(), int(portToSendTo.get()))

def getDataArrayToSend(fileToSend):
    dataArray = []
    while 1:
        chunk = fileToSend.read(128) #128 bit chunks
        dataArray.append(chunk)
        if not chunk:
            break
    return dataArray

# def createReceiveFileTread(socketToReceiveFileAt):
#     receiveFileThread = Thread(target=receiveFile, args=(socketToReceiveFileAt))
#     receiveFileThread.daemon = True
#     receiveFileThread.start()
#     thread.start_new_thread(receiveFile, (socketToReceiveFileAt, ));

# def receiveFile(socketToReceiveFileAt):
#     dataArray = RTPServer.receiveData(socketToReceiveFileAt)
#     print "Data Array of Length: " + str(len(dataArray))
#     RTPServer.writeDataArrayToFile(dataArray)

########################################
# CHECK PARAMETERS
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

rtpSocketManager = RTPSocketManager()

windowTitle = ""
if typeOfGUI == "client":
    rtpSocketManager.bindClient()
    windowTitle = "File Transfer Client"
elif typeOfGUI == "server":
    rtpSocketManager.bindServer()
    windowTitle = "File Transfer Server"
else:
    print "Please specify client or server"
    sys.exit()

firstSocket = rtpSocketManager.createSocket()

########################################
# INITIALIZATION
########################################

root = Tk()
root.geometry("400x500+100+100")
root.wm_title(windowTitle)

content = Frame(root, height=500, width=400)

machineInfoTitle = LabelFrame(content, text="Machine Info:", height=20, width=400, background='gray', borderwidth=0)
machineIPAddressLabel = Label(content, text="   IP Address:", justify=LEFT)
machineIPAddress = Label(content, text=str(socket.gethostbyname(socket.getfqdn())), justify=LEFT)
portsUsedLabel = Label(content, text="   Ports in Use:", justify=LEFT)

portsUsedStringVar = StringVar()
portsUsed = Label(content, textvariable=portsUsedStringVar, justify=LEFT)
portsUsedStringVar.set(rtpSocketManager.getPortsUsedString())

senderTitle = LabelFrame(content, text="Send Files:", height=20, width=400, background='gray', borderwidth=0)

emptyFrame0 = Frame(content, height=20, width=400)

sendToIP = Label(content, text="   Send To IP:", justify=LEFT)
ipToSendTo = StringVar()
ipToSendToEntry = Entry(content, textvariable=ipToSendTo)

sendToPort = Label(content, text="   Send To Port:")
portToSendTo = StringVar()
portToSendToEntry = Entry(content, textvariable=portToSendTo)

usingPort = Label(content, text="   Using Port:")
portToUse = StringVar()
usingPortEntry = Entry(content, textvariable=portToUse)

emptyFrame1 = Frame(content, height=20, width=400)

fileLocationPath = StringVar()
fileLocationLable = Label(content, textvariable=fileLocationPath) #background='blue'
fileLocationPath.set("   No file selected...")
chooseFileButton = Button(content, text="Choose File", anchor=CENTER, padx=10, pady=4, command= lambda: chooseFile())

emptyFrame2 = Frame(content, height=20, width=400)

sendFileButton = Button(content, text="SEND", anchor=CENTER, padx=10, pady=5, command= lambda: sendFile())

emptyFrame3 = Frame(content, height=20, width=400)

receiverTitle = LabelFrame(content, text="Receive Files:", height=20, width=400, background='gray', borderwidth=0)


########################################
# LAYOUT
########################################

content.grid(column=0, row=0, columnspan=3, rowspan=16)

machineInfoTitle.grid(row=0, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W)
machineIPAddressLabel.grid(row=1, column=0, rowspan=1, columnspan=1, sticky=Tkinter.W+Tkinter.N+Tkinter.S)
machineIPAddress.grid(row=1, column=1, rowspan=1, columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
portsUsedLabel.grid(row=2, column=0, rowspan=1, columnspan=1, sticky=Tkinter.W+Tkinter.N+Tkinter.S)
portsUsed.grid(row=2, column=1, rowspan=1, columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)

senderTitle.grid(row=3, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W)

emptyFrame0.grid(row=4, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)

sendToIP.grid(row=5, column=0, rowspan=1, columnspan=1, sticky=Tkinter.W+Tkinter.N+Tkinter.S)
ipToSendToEntry.grid(row=5, column=1, rowspan=1, columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
sendToPort.grid(row=6, column=0, rowspan=1, columnspan=1, sticky=Tkinter.W+Tkinter.N+Tkinter.S)
portToSendToEntry.grid(row=6, column=1, rowspan=1, columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)

usingPort.grid(row=7, column=0, rowspan=1, columnspan=1, sticky=Tkinter.W+Tkinter.N+Tkinter.S)
usingPortEntry.grid(row=7, column=1, rowspan=1, columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)

emptyFrame1.grid(row=8, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
fileLocationLable.grid(row=9, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
chooseFileButton.grid(row=10, column=0, rowspan=1, columnspan=3, sticky=Tkinter.N+Tkinter.S)

emptyFrame2.grid(row=11, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
sendFileButton.grid(row=12, column=0, rowspan=1, columnspan=3, sticky=Tkinter.N+Tkinter.S)
emptyFrame3.grid(row=13, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)


receiverTitle.grid(row=14, column=0, rowspan=1, columnspan=3, sticky=Tkinter.W)

########################################
# RUN
########################################

root.mainloop()



