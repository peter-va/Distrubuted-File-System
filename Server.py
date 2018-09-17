import socket # networking module
import sys
import os
import threading

def sysStart(hostList, portNum):
    global serSock, serPort, serHosts, threadList # set up globals
    serSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
    serPort = portNum
    serHosts = hostList
    serSock.bind(("", serPort))
    serSock.listen(5)
    threadList = [] # no client threads yet
    
    while True: # continuously allow connections
        try:
	    	clientConn,address = serSock.accept()
        except KeyboardInterrupt: # control-c
	    	try:
				if threading.activeCount() == 1: # kill server if control-c with no active clients
		    		break
	    	except KeyboardInterrupt: # kill everything if contorl-c pressed again
				sys.exit()
		newClient = srvr(clientConn) # make new client thread
        threadList.append(newClient) # add client to list
        newClient.start() # start client
    
def sysStop(hostList):
    for thread in threadList: # join all dead threads
        thread.join()
    serSock.close() # close server
    print "Client Closed"

class srvr(threading.Thread):
    origHost = None # global for original host
    threadLock = threading.Lock()
    def __init__(self,newConn):
        threading.Thread.__init__(self)
        self.FPList = {} # file pointer dictionary
        self.origHost = socket.gethostname() # set original host
        self.clientConn = newConn # hold connections
    
    def toHashHost(self,fileName):
        if self.origHost != socket.gethostname(): # return to original host if not there
            os.system("exit &") # do in background
            os.chdir("/tmp")
        
        if str(socket.gethostname()) != serHosts[hash(fileName) % len(serHosts)]: # if not in correct host for file
            os.system("ssh "+serHosts[hash(fileName) % len(serHosts)]+" &") # move to correct host
            os.chdir("/tmp")
	
    
    def getFunc(self, data):
    	func = data.split("(")[0] # function name
    	fileName = data.split("(")[1].split(",")[0].split(")")[0] # file name
    	try:
            bytesRW = data.split(",")[1].split(")")[0] # read/write argument if it exists
    	except:
            bytesRW = ""
    	return (func, fileName, bytesRW) # return 3 values
    
    def dOpen(self,fileName):
        self.toHashHost(fileName) # to correct host
        try:
            a = open(fileName, 'r+') # file exists
        except IOError:
            a = open(fileName, 'a+') # file doesn't exist
        self.FPList[fileName] = a # set new entry for file pointer list
        return "Opened "+fileName
    
    def dRead(self,fileName,bytesToRead):
        self.toHashHost(fileName)
        fp = self.FPList[fileName] # grab file pointer
        readBytes = fp.read(int(bytesToRead)) # read number of bytes
        return readBytes # return read bytes
    
    def dWrite(self, fileName, bytesToWrite):
        self.toHashHost(fileName)
        fp = self.FPList[fileName] # grab file pointer
        fp.write(bytesToWrite) # write given bytes
        return "Wrote \""+bytesToWrite+"\" to "+fileName
    
    def dClose(self, fileName):
        self.toHashHost(fileName)
        fp = self.FPList[fileName] # grab file pointer
        fp.close() # close file
        del self.FPList[fileName] # remove file pointer from list
        return "Closed "+fileName
    
    def run(self):
        os.chdir("/tmp") # make sure we're in /tmp
        while 1: # run until killed
            clientInput = self.clientConn.recv(1000)
            if clientInput == "" or clientInput == "done": # kill connection if necessary
                break
            clientInput = self.getFunc(clientInput)
            if clientInput[0] == "dOpen": # run correct function based on input
                clientOutput = self.dOpen(clientInput[1])
            elif clientInput[0] == "dRead":
                clientOutput = self.dRead(clientInput[1],clientInput[2])
            elif clientInput[0] == "dWrite":
                clientOutput = self.dWrite(clientInput[1],clientInput[2])
            elif clientInput[0] == "dClose":
                clientOutput = self.dClose(clientInput[1])
            else:
                clientOutput = "Failed Command"
            srvr.threadLock.acquire() # critical section
            self.clientConn.send(clientOutput)
            srvr.threadLock.release() # end critical section
    
        self.clientConn.close() # kill once out
	numClients = threading.activeCount() - 2 # get current clients
        print "client connection closed"
	print str(numClients) + " currently active client connections" # tell server user how many clients left
        return

