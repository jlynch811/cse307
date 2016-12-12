#Jonathan Lynch
#109030898
#Client Implementation

from socket import *
import sys
import pickle
import _thread
import os
#from Database import *

serverName = 'localhost'
serverPort = 5898
debug=1
connectionStatus = 0
currentCmd = ""
nValue = 5
startRange = 0
endRange = 4
clientSocket = socket(AF_INET, SOCK_STREAM)
name = ""
uid = 0
subPath = r'Subs/'
postCountPath = r'SubPosts/'
readPostsPath = r'ReadPosts/'
currentDisplay = []
currentGroup = ""
postList = []

#Structures

class Package:
	def __init__(self, protocol, objlist, name):
		self.protocol = protocol
		self.list = objlist
		self.name = name
class Group:
	def __init__(self, gid, name):
		self.gid = gid
		self.name = name

class Post: 
	def getTimeStamp(self):
		return 0.1
	def __init__(self, pid, subject, body, userid):
		self.pid = pid
		self.subject = subject
		self.body = body
		self.userid = userid
		self.time = self.getTimeStamp()

def byIsRead_key(post):
	return isPostRead(post.subject)

def nextN():
	global startRange
	global endRange
	global nValue

	startRange = startRange + nValue
	endRange = endRange + nValue

def sendNextN(protocol):
	nextN()
	message = protocol + " " + str(startRange) + " " + str(endRange)
	sendEncoded(clientSocket, message)

def postNextN():
	nextN()

def subNextN():
	nextN()
	handleSubscribedGroups("")

def resetNValue(n):
	global startRange
	global endRange
	global nValue

	nValue = n
	startRange = 0
	endRange = nValue-1

def handleInput(i):
	global currentCmd
	global nValue

	cmdList = i.split()

	#Check if we're in a command "mode." These return immediately after executing
	#if(connectionStatus ==1):
		#runTests()

	#SUB AG COMMANDS
	if(currentCmd == "ALLGROUPS"):
		handleAllGroupsSubCommand(cmdList)
		return

	elif(currentCmd == "SUBGROUPS"):
		handleSubscribedGroupsSubCommand(cmdList)
		return

	elif(currentCmd == "READGROUP"):
		handleReadGroupSubCommand(cmdList)
		return


	#Login Command
	elif(cmdList[0] == "login" and len(cmdList)==2):
		if(debug): print("Calling Login", cmdList[1])

		handleLogin(cmdList[1])

	elif(cmdList[0] == "help"):
		handleHelp()

	#Disallow other commands if not logged in.
	elif(connectionStatus==0):
		print("Unrecognized Command")
		return

	#Logout Command
	elif(cmdList[0] == "logout"):
		if(debug): print("Calling Logout")
		handleLogout()

	#Exit Command
	elif(cmdList[0] == "exit"):
		print("Exiting...")
		sys.exit()

	#ag Command
	elif(cmdList[0] == "ag" and (len(cmdList)==1 or len(cmdList)==2)):
		#Set the optional nValue
		if(len(cmdList)==2):
			resetNValue(int(cmdList[1]))
			if(debug): print("nValue set: ", nValue)

		handleAllGroups(cmdList)

	#sg Command
	elif(cmdList[0] == "sg" and (len(cmdList)==1 or len(cmdList)==2)):
		#Set the optional nValue
		if(len(cmdList)==2):
			resetNValue(int(cmdList[1]))
			if(debug): print("nValue set: ", nValue)

		handleSubscribedGroups(cmdList)

	#rg Command
	elif(cmdList[0] == "rg" and (len(cmdList)==2 or len(cmdList)==3)):
		#Set the optional nValue
		if(len(cmdList)==3):
			resetNValue(int(cmdList[2]))
			if(debug): print("nValue set: ", nValue)

		handleReadGroup(cmdList)

	else:
		print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")

#Multithreading to support stdin and server input
def recvFunc(threadName, val):
	while True:

		t = clientSocket.recv(10000)
		p  = pickle.loads(t)
		protocol = p.protocol
		list = p.list
		print(list)
		handleServerInput(protocol, list)

def handleServerInput(protocol, list):
	global currentDisplay
	global postList

	if(debug): print("PROTOCOL: ", protocol)


	if(protocol=="ALLGROUPS"):
		currentDisplay = list
		displayAllGroups()

	if(protocol=="READGROUP"):
		postList = list

		for post in postList:

			print("SUBJECT: ", post.subject)
			print("TIME: ", post.time)
			print("BODY: ", post.body)

		sortPosts()
		displayPosts()

def displayAllGroups():
	count = 0
	for group in currentDisplay:
		print(str(count+1)+ ". ("+amSubscribedPrint(group.name)+") "+ group.name)
		count+=1
def displaySubGroups():
	global currentDisplay
	count = 0
	for groupname in currentDisplay:
		pCount = getPostCount(groupname)
		c = int(pCount)
		newS =  str(count+1)+ ".\t" + str(c)+"\t"+ groupname
		print(newS)
		count+=1

def displayPosts():
	global postList
	global nValue
	global startRange
	global endRange

	c= startRange
	count = 0

	for post in postList:
		if(count>=startRange and count<=endRange):
			print(str(count+1) + ". " + displayPostRead(post.subject) + " " + str(post.time) + " " + post.subject)
		count = count+1
		c = c+1

def sortPosts():
	global postList

	postList = sorted(postList, key=byIsRead_key)
	print("TEST")


def stripEndTags(s):
	if(s.endswith('\r')):
		s = s[:2]
	if(s.endswith('\n')):
		s = s[:2]
	if(s.endswith('\r')):
		s = s[:2]

	return s

def handleLogin(username):
    global connectionStatus
    global name
    global clientSocket

    #Only attempt to connect if we're not already connected.
    if(connectionStatus==0):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))

        loginRequest = "LOGIN " + str(username) 
        print("Waiting to send...")
        sendEncoded(clientSocket, loginRequest)
        print("Sent...")
        modifiedSentence = clientSocket.recv(1024)
        print ('From Server:', modifiedSentence)

        name = username
        connectionStatus = 1
        _thread.start_new_thread(recvFunc, ("recvThread",2,))

        # Check to see if this is a returning user. If not, add a new user to the users.json file

    else:
        print("Already logged in")

def handleHelp():
	print("\n\t\t---COMMAND DIRECTORY---\n")
	print("login <username>\t\tLogs in as <username>")
	print("help\t\t\t\tDisplays this menu")
	print("\n\t\t-COMMANDS REQUIRING LOGIN-\n")
	print("ag [<N>]\t\t\tLists all existing groups, N at a time")
	print("\tSUB COMMANDS")
	print("\ts <1 2 3 ... N>\t\tSubscribes to selected groups")
	print("\tu <1 2 3 ... N>\t\tUnsubscribes from selected groups")
	print("\tn\t\t\tLists next N discussion groups")
	print("\tq\t\t\tExits ag command")
	print("")
	print("sg [<N>]\t\t\tLists all subscribed groups, N at a time")
	print("\tSUB COMMANDS")
	print("\tu <1 2 3 ... N>\t\tUnsubscribes from selected groups")
	print("\tn\t\t\tLists next N subscribed discussion groups")
	print("\tq\t\t\tExits sg command")
	print("")
	print("rg <gname> [<N>]\t\tDisplays status of N posts in group <gname>")
	print("\tSUB COMMANDS")
	print("\t<id>\t\t\tDisplays contents of post <id>")
	print("\t\tSUB COMMANDS")
	print("\t\tn\t\tDisplays next N lines of the post")
	print("\t\tq\t\tQuit displaying post content")
	print("")
	print("\tr <X> | <X-Y>\t\tMarks <X> post, or <X> to <Y> posts as read")
	print("\tn\t\t\tDisplays next N posts")
	print("\tp\t\t\tPosts to the group")
	print("\tq\t\t\tExits rg command")
	print("")
	print("logout\t\t\t\tLogs out user and terminates client")
	print("")


#Set the current Command to ALLGROUPS
def handleAllGroups(cmdList):
	global currentCmd
	global nValue

	currentCmd = "ALLGROUPS"
	message = currentCmd + " " + str(startRange) + " " + str(endRange)
	sendEncoded(clientSocket, message)

#Handle ALLGROUPS sub Commands
def handleAllGroupsSubCommand(cmdList):
	global currentCmd
	global nValue

	if(debug): print("All Groups Sub Command")

	message = ""

	#Ensure less than n sized arguments
	if(cmdList[0] == "s" and len(cmdList)<= nValue+1):
		message = "SUB"
		sCommand(cmdList)

	elif(cmdList[0] == "u" and len(cmdList)<= nValue+1):
		message = "UNSUB"
		uCommand(cmdList)

	elif(cmdList[0] == "n"):
		sendNextN("ALLGROUPS")

	elif(cmdList[0] == "q"):
		currentCmd = ""

	else:
		print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")


#Set the current Command to SUBGROUPS
def handleSubscribedGroups(cmdList):
    global currentCmd
    global nValue
    global currentDisplay

    currentCmd = "SUBGROUPS"
    print("RANGE: ", startRange, endRange)
    subList = getSubGroups(startRange, endRange)
    currentDisplay = subList
    print(subList)
    print(currentDisplay)
    displaySubGroups()



    # Get the subscribed groups for the current user and print them up to N
    #discussionGroups = getDiscussionGroups(name)
	#for i in range(0, cmdList):
        #print i + ".\t" + discussionGroups[i]['name']

def getSubGroups(start, end):
	fileName = subPath + name+"sub.txt"
	f = open(fileName,"r+")
	d = f.readlines()
	f.seek(0)

	ret = []
	count = 0
	for i in d:
	    if(count>=start and count <=end):
	    	ret = ret + [i]
	    count+=1

	f.close()

	return ret


#Handle SUBGROUPS sub Commands
def handleSubscribedGroupsSubCommand(cmdList):
	global currentCmd
	global nValue

	if(debug): print("Sub Groups Sub Command")

	message = ""

	#Ensure less than n sized arguments
	if(cmdList[0] == "u" and len(cmdList)<= nValue+1):
		message = "UNSUB"
		uCommandSub(cmdList)
		return

	elif(cmdList[0] == "n"):
		subNextN()
		return

	elif(cmdList[0] == "q"):
		currentCmd = ""
		print("Exiting sub commands")
		return

	print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")

def uCommand(cmdList):
	for val in cmdList[1:]:
		print("VAL: ", val)
		try:
			val = int(val)
			val = val - 1
		except:
			print("Incorrect Format")
			return
		try:
			unsubscribeToGroup(currentDisplay[val].name)
		except: print("Unable to unsubscribe from group (Likely out of range index)")

def uCommandSub(cmdList):
	for val in cmdList[1:]:
		print("VAL: ", val)
		try:
			val = int(val)
			val = val - 1
		except:
			print("Incorrect Format")
			return
		print("CUR DISPLAY: ", currentDisplay[val])
		unsubscribeToGroup(currentDisplay[val])

def sCommand(cmdList):
	for val in cmdList[1:]:
			try:
				val = int(val)
				val = val - 1
			except:
				print("Incorrect Format")
				return
			try:
				subscribeToGroup(currentDisplay[val].name)
			except: print("Unable to subscribe to group (Likely out of range index)")


#Set the current Command to READGROUP
def handleReadGroup(cmdList):
	global currentCmd
	global nValue
	global currentGroup

	currentCmd = "READGROUP"
	currentGroup = cmdList[1]
	resetNValue(nValue)
	message = currentCmd + " " + cmdList[1]
	sendEncoded(clientSocket, message)

#Handle READGROUP sub Commands
def handleReadGroupSubCommand(cmdList):
	global currentCmd
	global nValue
	global currentGroup

	if(debug): print("Read Groups Sub Command")

	message = ""

	#Mark Read Command
	if(cmdList[0] == "r" and (len(cmdList) == 2)):
		rangeList = cmdList[1].split("-")

		if(debug): print("RANGELIST: ", rangeList)

		#Single Value. Just send
		if(len(rangeList)==1):
			message = "MARKREAD " + str(rangeList[0])
			markPostRead(int(rangeList[0])-1)
			sortPosts()
			resetNValue(nValue)
			displayPosts()
			return

		#Check format of rangelist and [0] < [1]
		elif(len(rangeList)==2 and int(rangeList[0]) < int(rangeList[1])):
			message = "MARKRANGEREAD " + str(rangeList[0]) + " " + str(rangeList[1])
			markPostRangeRead(int(rangeList[0])-1, int(rangeList[1]))
			sortPosts()
			resetNValue(nValue)
			displayPosts()
			return

		else:
			print("Format Error On r Command")
			return

	#List Next N Posts Command
	if(cmdList[0] == "n" and len(cmdList) == 1):

		postNextN()
		displayPosts()
		return

	#Post to Group Command
	if(cmdList[0] == "p" and len(cmdList) == 1):
		postBody = ""
		

		subjectStr = input("Enter Post Subject.\n")
		currentStr = input("Enter Post Body followed by a . on its own line.\n")

		while(currentStr != "."):
			postBody = postBody + currentStr+"\n"
			currentStr = input("")

		print("SUBJECT: \n", subjectStr)
		print("POST BODY: \n", postBody)

		postList = [subjectStr, postBody]
		sendPost(subjectStr, postBody)

	#Quit RG Command
	if(cmdList[0] == "q"):
		currentCmd = ""
		currentGroup = ""
		postList = []

	#[id] command
	else:
		try:
			if(int(cmdList[0]) >=1 and int(cmdList[0]) <= nValue):
				message = "ID " + cmdList[0]
				print("ID: ", cmdList[0])
				sendEncoded(clientSocket, message)
		except:
			print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")
			return

def sendPost(subject, content):
	p = [Post(None, subject, content, name)]
	package = Package("MAKEPOST", p, currentGroup)
	pickledPost = pickle.dumps(p)
	clientSocket.send(pickledPost)


def handleLogout():
	global connectionStatus

	message = "LOGOUT " + str()
	sendEncoded(clientSocket, "LOGOUT " + str(name))
	if(debug): print("SENT COMMAND: ", message)

	clientSocket.shutdown(SHUT_WR)
	#Wait for confirmation to close
	logout = clientSocket.recv(1024)

	clientSocket.close()
	connectionStatus = 0


def sendEncoded(socket, message):
	if(debug): print("Sending Message: ", message)
	socket.send(str.encode(message))


def subscribeToGroup(gname):
	initSubFile()
	if(amSubscribed(gname)):
		print("Already Subscribed to ", gname)
		return

	fileName = subPath + name+"sub.txt"
	subFile = open(fileName, 'a+')

	subFile.write(gname+"\n")
	subFile.close()
	initPostCount(gname)

def unsubscribeToGroup(gname):
	fileName = subPath + name+"sub.txt"
	f = open(fileName,"r+")
	d = f.readlines()
	f.seek(0)
	for i in d:
		print("i: ", i.encode())
		print("gname: ", gname.encode())
		if (i != gname +"\n" and i!=gname):
			f.write(i)
	f.truncate()
	f.close()

	removePostCount(gname)

def amSubscribed(gname):
	#if(debug): print("Am Subscribed Check: ", gname.encode())

	initSubFile()

	fileName = subPath + name + "sub.txt"
	with open(fileName, 'r+b') as subFile:

		for line in subFile:
			if(line==gname.encode() +b'\r\n'):
				return 1
			elif(line==gname.encode()):
				return 1
	return 0

def amSubscribedPrint(gname):
	if(amSubscribed(gname)):
		return "s"
	return " "

def initSubFile():
	fileName = subPath + name + "sub.txt"
	subFile = open(fileName, 'a+')
	subFile.close()

	fileName = postCountPath + name + "count.txt"
	countFile = open(fileName, 'a+')
	countFile.close()

	fileName = readPostsPath + name + "posts.txt"
	postsFile = open(fileName, 'a+')
	postsFile.close()

def initDirs():
	directory = "Subs"
	if not os.path.exists(directory):
		os.makedirs(directory)

	directory = "SubPosts"
	if not os.path.exists(directory):
		os.makedirs(directory)

	directory = "ReadPosts"
	if not os.path.exists(directory):
		os.makedirs(directory)


def initPostCount(gname):
	print("InitPostCount")
	fileName = postCountPath + name + "count.txt"

	countFile = open(fileName, 'a+')

	countFile.write(gname+"\n")
	countFile.write("0\n")
	countFile.close()

def getPostCount(gname):
	fileName = postCountPath + name + "count.txt"
	f = open(fileName,"r+b")
	d = f.readlines()
	f.seek(0)

	#print(gname)
	gname = stripEndTags(gname)

	g = 0
	for line in d:
		l = line.decode()
		line = stripEndTags(line.decode())

		#print("LINE: ",line)
		#print("GNAME: ", gname)
		if(g==1):
			f.close()
			return l
		elif(line==gname):
			#print("FOUND IT")
			g = 1
	f.close()

	return "111"



def removePostCount(gname):
	fileName = postCountPath + name + "count.txt"
	with open(fileName, 'a+b') as countFile:

		lineNo = -1
		d = countFile.readlines()
		countFile.seek(0)
		count=0
		for line in countFile:
			count = count+1
			if(count%2!=0):
				if(line==gname.encode() +b'\r\n'):
					lineNo = count

	#Remove the line and the next
	if(lineNo!=-1):
		removeLine(fileName,lineNo)
		removeLine(fileName,lineNo)

def removeLine(fileName, lineNo):
	f = open(fileName,"r+")
	d = f.readlines()
	f.seek(0)
	count = 1
	for i in d:
	    if(lineNo != count):
	    	f.write(i)
	    count = count + 1
	f.truncate()
	f.close()

def markPostRead(postNum):
	global postList

	post = postList[postNum].subject
	if(isPostRead(post)):
		return

	fileName = readPostsPath + name+"posts.txt"
	postsFile = open(fileName, 'a+')

	postsFile.write(post+"\n")
	postsFile.close()

def markPostRangeRead(start, end):

	for i in range(start, end):
		markPostRead(i)

def isPostRead(postName):
	initSubFile()

	fileName = readPostsPath + name + "posts.txt"
	with open(fileName, 'r+b') as postsFile:

		for line in postsFile:
			if(line==postName.encode() +b'\r\n'):
				return 1
			elif(line==postName.encode()):
				return 1
	return 0

def displayPostRead(postName):
	if(isPostRead(postName)):
		return " "
	return "N"


def runTests():
	print("RUNNING TESTS: ")
	subscribeToGroup("testgroup");
	subscribeToGroup("testgroup2");
	subscribeToGroup("testgroup3");



	#removePostCount("test2")


#Program loop
initDirs()
while True:
    if sys.version_info >= (3,0):
        readInput = input('Enter command: ')
    else:
        readInput = raw_input('Enter command: ')
        
    handleInput(readInput)