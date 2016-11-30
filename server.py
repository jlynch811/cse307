# CSE 310 Group Project
# Jonathan Lynch 109030898

from socket import *
import select
import sys
import _thread
import pickle

serverPort = 5898
serverSocket = socket(AF_INET,SOCK_STREAM)
debug=1

socketList = []
outputSocketList = []

def acceptFunc(threadName, val):
	print("Accept Func!")

def sendEncoded(socket, message):
	print("Sending Message: ", message)
	socket.send(str.encode(message))

serverSocket.setblocking(0)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

socketList = socketList + [serverSocket]

#_thread.start_new_thread( acceptFunc, ("AcceptThread",2,))
#connectionSocket, addr = serverSocket.accept()
#socketList = socketList + [connectionSocket]

def handleUserCommand(command):
	cmdList = command.split()

	if(cmdList[0]=="ag"):
		print("CMD recognized: ", cmdList[0])

#This is for receiving an array over socket, required for post[subject, body]
def isPickle(s):
	cmdList = s.split()
	print(cmdList[0])
	if(cmdList[0] == b"PICKLE"):
		return 1
	else: return 0

while socketList:
	readSockets, writeSockets, exceptSockets = select.select(socketList, outputSocketList, socketList)

	for s in readSockets:

		#New Connection if serverSocket
		if s is serverSocket:
			connection, client_address = s.accept()
			print("NEW CONNECTION: ", client_address)
			connection.setblocking(0)
			socketList = socketList + [connection]

		#Not server socket. Handle what client sent
		else:
			message = s.recv(1024) 
			print("Received from client: ", message)

			#CHECK FOR EOF
			if(not message):
				print("RECEIVED EOF")
				sendEncoded(s, "LOGOUT")	
				s.close()
				socketList.remove(s)


			elif(isPickle(message)):
				message = message[7:]
				print("PICKLE MESSAGE:\n", pickle.loads(message))


			else:
				s.send(message)
				handleUserCommand(str(message))


'''while True:
	print ('Ready to serve...')
	 #Fill in start #Fill in end
	try:
		message = connectionSocket.recv(1024) 

		print("Received from client: ", message)

		connectionSocket.send(message)

	except IOError:
		#Send response message for file not found
		#Fill in start
		connectionSocket.send(str.encode("HTTP://1.1 404 NOT FOUND\r\n\r\n"))
		connectionSocket.send(str.encode("404 Not Found"))
		#Fill in end
		#Close client socket
		#Fill in start
		connectionSocket.close()
		print("Socket Closed")
		#Fill in end 
serverSocket.close()
print("Socket Closed")'''