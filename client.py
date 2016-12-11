#Jonathan Lynch
#109030898
#Client Implementation

from socket import *
import sys
import pickle
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

def nextN():
	global startRange
	global endRange
	global nValue

	startRange = startRange + nValue
	endRange = endRange + nValue

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

		for val in cmdList[1:]:
			message = message + " " + val
		print("MESSAGE: ", message)
		sendEncoded(clientSocket, message)

	elif(cmdList[0] == "u" and len(cmdList)<= nValue+1):
		message = "UNSUB"

		for val in cmdList[1:]:
			message = message + " " + val
		sendEncoded(clientSocket, message)

	elif(cmdList[0] == "n"):
		message = "NEXTN " + str(nValue)
		sendEncoded(clientSocket, message)

	elif(cmdList[0] == "q"):
		currentCmd = ""

	else:
		print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")


#Set the current Command to SUBGROUPS
def handleSubscribedGroups(cmdList):
    global currentCmd
    global nValue

    currentCmd = "SUBGROUPS"
    message = currentCmd + " " + str(nValue)
    sendEncoded(clientSocket, message)

    # Get the subscribed groups for the current user and print them up to N
    #discussionGroups = getDiscussionGroups(name)
	#for i in range(0, cmdList):
        #print i + ".\t" + discussionGroups[i]['name']

#Handle SUBGROUPS sub Commands
def handleSubscribedGroupsSubCommand(cmdList):
	global currentCmd
	global nValue

	if(debug): print("Sub Groups Sub Command")

	message = ""

	#Ensure less than n sized arguments
	if(cmdList[0] == "u" and len(cmdList)<= nValue+1):
		message = "UNSUB"

		for val in cmdList[1:]:
			message = message + " " + val
		sendEncoded(clientSocket, message)

	elif(cmdList[0] == "n"):
		message = "NEXTN " + str(nValue)
		sendEncoded(clientSocket, message)

	elif(cmdList[0] == "q"):
		currentCmd = ""

	print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")

#Set the current Command to READGROUP
def handleReadGroup(cmdList):
	global currentCmd
	global nValue

	currentCmd = "READGROUP"
	message = currentCmd + " " + cmdList[1] + " " + str(nValue)
	sendEncoded(clientSocket, message)

#Handle READGROUP sub Commands
def handleReadGroupSubCommand(cmdList):
	global currentCmd
	global nValue

	if(debug): print("Read Groups Sub Command")

	message = ""

	#Mark Read Command
	if(cmdList[0] == "r" and (len(cmdList) == 2)):
		rangeList = cmdList[1].split("-")

		if(debug): print("RANGELIST: ", rangeList)

		#Single Value. Just send
		if(len(rangeList)==1):
			message = "MARKREAD " + str(rangeList[0])

		#Check format of rangelist and [0] < [1]
		elif(len(rangeList)==2 and int(rangeList[0]) < int(rangeList[1])):
			message = "MARKRANGEREAD " + str(rangeList[0]) + " " + str(rangeList[1])

		else:
			print("Format Error On r Command")
			return
		sendEncoded(clientSocket, message)

	#List Next N Posts Command
	if(cmdList[0] == "n" and len(cmdList) == 1):

		message = "NEXTN " + str(nValue)
		sendEncoded(clientSocket, message)

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

		#Pickle is used to send the array over the socket.
		pickledPost = pickle.dumps(postList)
		clientSocket.send(str.encode("PICKLE ") + pickledPost)

	#Quit RG Command
	if(cmdList[0] == "q"):
		currentCmd = ""

	#[id] command
	else:
		try:
			if(int(cmdList[0]) >=1 and int(cmdList[0]) <= nValue):
				message = "ID " + cmdList[0]
				sendEncoded(clientSocket, message)
		except:
			print("Unrecognized Command, Incorrect Format, Or Command Is Not Available At This Time")
			return

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
	if(amSubscribed(gname)):
		print("Already Subscribed to ", gname)
		return

	fileName = subPath + name+"sub.txt"
	subFile = open(fileName, 'a+')

	subFile.write(gname+"\n")

def unsubscribeToGroup(gname):
	fileName = subPath + name+"sub.txt"
	f = open(fileName,"r+")
	d = f.readlines()
	f.seek(0)
	for i in d:
	    if i != gname +"\n":
	    	f.write(i)
	f.truncate()
	f.close()

	removePostCount(gname)

def amSubscribed(gname):
	if(debug): print("Am Subscribed Check: ", gname)

	fileName = subPath + name + "sub.txt"
	with open(fileName, 'a+b') as subFile:

		for line in subFile:
			if(line==gname.encode() +b'\r\n'):
				return 1
	return 0


def initPostCount(gname):
	print("InitPostCount")


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


def runTests():
	print("RUNNING TESTS: ")
	subscribeToGroup("testgroup");
	subscribeToGroup("testgroup3");

	unsubscribeToGroup("testgroup2");

	amSubscribed("testgroup3")

	#removePostCount("test2")



#Program loop
while True:
    if sys.version_info >= (3,0):
        readInput = input('Enter command: ')
    else:
        readInput = raw_input('Enter command: ')
        
    handleInput(readInput)