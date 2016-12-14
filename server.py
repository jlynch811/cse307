# CSE 310 Group Project
# Jonathan Lynch 109030898

import datetime
import Database2
from socket import *
import select
import sys
import _thread
import pickle

#Structures
class Package:
	def __init__(self, protocol, objlist, name):
		self.protocol = protocol
		self.objlist = objlist
		self.name = name

class Group:
	def __init__(self, gid, name):
		self.gid = gid
		self.name = name

class Post: 
	def __init__(self, pid, subject, body, userid, gname):
		self.pid = pid
		self.subject = subject
		self.body = body
		self.userid = userid
		self.time = self.getTimeStamp()
		self.gname = gname

	def getTimeStamp(self):
		return format(datetime.datetime.now())

#Program
serverPort = 5898
serverSocket = socket(AF_INET,SOCK_STREAM)
debug=1

#Lists

#Loads all groups from database into program
def loadGroups(filePath):
	return Database2.loadDiscussionGroups()

#Load all posts from database into program
def loadPosts(filePath):
	return Database2.loadPosts()

#Sockets and post/group data
groupList = loadGroups("no current filepath")
postList = loadPosts("no current filepath")
socketList = []
outputSocketList = []

#Helper Functions

def acceptFunc(threadName, val):
	print("Accept Func!")

def sendEncoded(socket, message):
	print("Sending Message: ", message)
	socket.send(str.encode(message))

#Gets all the posts in a particular group
def getGroupPosts(gname):
	toSend = []

	for post in postList:
		if(post.gname == gname):
			toSend.append(post)

	return toSend


#This is for receiving an array over socket, required for post[subject, body]
def isPickle(s):
	cmdList = s.split()
	print(cmdList[0])
	if(cmdList[0] == b"PICKLE"):
		return 1
	else: return 0

#Sends a serialized stream of data to the client
#currsocket - client socket
#prefix - protocol
#obj - object to be sent
def pickleSend(currsocket, prefix, obj):
	#Pickle is used to send the array over the socket.
	p = Package(prefix, obj, None)
	pickledObj = pickle.dumps(p)
	currsocket.send(pickledObj)

#Sends a serialized stream of data to the client
#currsocket - client socket
#prefix - protocol
#obj - object to be sent
#name - name of the object
def pickleSendPost(currsocket, prefix, obj, name):
	#Pickle is used to send the array over the socket.
	p = Package(prefix, obj, name)
	pickledObj = pickle.dumps(p)
	currsocket.send(pickledObj)

#Function to handle all of the sent commands
def handleUserCommand(command, currsocket):
	cmdList = command.split(None, 1)

	if(cmdList[0] == "ALLGROUPS"):
		handleAG(cmdList[1], currsocket)

	elif(cmdList[0] == "LOGIN"):
		currsocket.send(command.encode())

	elif(cmdList[0] == "READGROUP"):
		handleRG(cmdList[1], currsocket)

	elif(cmdList[0] == "POSTCOUNT"):
		handlePostCount(cmdList[1], currsocket)

#Handles the AG command
def handleAG(info, currsocket):
	infoList = info.split()
	indices = groupList[ int(infoList[0]) : (int(infoList[1]) + 1) ]
	pickleSend(currsocket, "ALLGROUPS", indices)

#Handles RG command
def handleRG(info, currsocket):
	infoList = info.split()
	gname = infoList[0]

	toSend = []

	for post in postList:
		if(post.gname == gname):
			toSend.append(post)

	pickleSend(currsocket, "READGROUP", toSend)

#Handles sending postcount to the client
def handlePostCount(info, currsocket):
	infoList = info.split()
	gname = infoList[0]

	toSend = []
	toSendCount = 0

	for post in postList:
		if(post.gname == gname):
			toSendCount+=1

	print("SENDCOUNT: ", toSendCount)
	pickleSendPost(currsocket, "POSTCOUNT", toSendCount, gname)

#Handles decoding a sent pickle from the client
#Only used when client needs to upload a post to the server
#Then broadcasts a announcement protocol to all clients
def handlePostCommand(package, currsocket, allsockets, serversocket):
	if(package.protocol == "MAKEPOST"):
		postList.append(package.objlist)
		Database2.appendPost(package.objlist)

		pickleSend(currsocket, "MAKEPOST", "SUCCESS")

		thePost = package.objlist
		currGroup = package.objlist.gname
		toSend = getGroupPosts(currGroup)

		print("Current Group: "+str(currGroup)+" | Number of Posts: "+str(toSend))

		for s in allsockets:
			if not(s is serversocket):
				print("\n\ns: ", str(s) + "\n\n")
				pickleSendPost(s, "NEWPOST", len(toSend), thePost)

		pickleSend(currsocket, "CONFIRMPOST", None)

#Main Program
serverSocket.setblocking(0)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

socketList = socketList + [serverSocket]

#_thread.start_new_thread( acceptFunc, ("AcceptThread",2,))
#connectionSocket, addr = serverSocket.accept()
#socketList = socketList + [connectionSocket]

#Select loop, loops to receive messages from client
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
			try:
				message = s.recv(1024) 
				print("Received from client: ", message)

				#CHECK FOR EOF
				if(not message):
					print("RECEIVED EOF")
					#sendEncoded(s, "LOGOUT")	
					pickleSend(s, "LOGOUT", None)
					s.close()
					socketList.remove(s)

				else:
					#s.send(message)
					try: 
						message = pickle.loads(message)
						handlePostCommand(message, s, socketList, serverSocket)
					except: 
						handleUserCommand(message.decode(), s)
			except ConnectionResetError:
				s.close()
				socketList.remove(s)

	
			