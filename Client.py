import socket
import sys

global cliHost, cliPort, cliConn
cliConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up client socket
cliHost = sys.argv[1] # host name
cliPort = int(sys.argv[2]) # port num
cliConn.connect((cliHost, cliPort)) # connect

while(1):
    input = raw_input(">> ")
    if input == "done": # end client
        break
    cliConn.send(input) # send input
    data = cliConn.recv(1000000) # receive output
    print data
    if not data: # kill client if nothing received
        break

cliConn.close() # official close of client

