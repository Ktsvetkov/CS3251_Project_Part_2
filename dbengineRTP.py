import sqlite3, sys
from sqlite3 import *
import socket
from RTPSocket import RTPSocket
from RTPSocketManager import RTPSocketManager
from RTPPacket import RTPPacket

#Check arguments length is valid
if len(sys.argv) < 2:
    print "Please use valid number of arguments"
    sys.exit()

#Create sqlite database and table and populate table
conn = sqlite3.connect("GtStudentDb.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS GtStudents( ID VARCHAR( 20 ), first_name VARCHAR( 20 ), last_name VARCHAR( 20 ), quality_points VARCHAR( 20 ), gpa_hours VARCHAR( 20 ), gpa VARCHAR( 20 ), PRIMARY KEY (ID))")
rows = [('903076259', 'Anthony', 'Peterson', '231', '63', '3.666667'),
        ('903084074', 'Richard', 'Harris', '236', '66', '3.575758'),
        ('903077650', 'Joe', 'Miller', '224', '65', '3.446154'),
        ('903083691', 'Todd', 'Collins', '218', '56', '3.892857'),
        ('903082265', 'Laura', 'Stewart', '207', '64', '3.234375'),
        ('903075951', 'Marie', 'Cox', '246', '63', '3.904762'),
        ('903084336', 'Stephen', 'Baker', '234', '66', '3.545455')]
cursor.executemany('replace into GtStudents values (?,?,?,?,?,?)', rows )
conn.commit()

#Get port number from parameters
try:
    serverPortNumber = int(sys.argv[1])
except Exception as e:
    print "Failure parsing parameters: " + str(e)
    sys.exit()

#socket() bind()
socketManager = RTPSocketManager()
socketManager.bindUDP(str(socket.gethostbyname(socket.getfqdn())), 8592)
socket = socketManager.createSocket(serverPortNumber)


#handle recv() and send()
print "The server is ready to receive"
while 1:

    #recv()
    ipAddress, portNumber, dataArray, description = socket.recvData()
    message = dataArray[0]

    #query sqlite database
    modifiedMessage = ""
    try:
        arrayAttributes = message.split(":")
        message = "SELECT " + arrayAttributes[1] + " FROM GtStudents WHERE ID = " + arrayAttributes[0]
        cursor = conn.execute(message)
        paramArray = arrayAttributes[1].split(",")
        j = 0
        for row in cursor:
            j = j +1
            i = 0
            for col in row:
                if i == 0:
                    modifiedMessage = modifiedMessage + paramArray[i] + ": " + col
                if i > 0:
                    modifiedMessage = modifiedMessage + "," + paramArray[i] + ": " + col
                i = i + 1
        if j == 0:
            modifiedMessage = "no such student id"
    except Exception as e:
        modifiedMessage = str(e)

    #send()
    socket.sendData(ipAddress, portNumber, [modifiedMessage])
    print "Sent Response: " + modifiedMessage




