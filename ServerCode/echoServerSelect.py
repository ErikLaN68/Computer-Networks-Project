#Networks Assignment - Server Select

from socket import *
import sys, select, os, time

# IP of local houst
serverIp = '127.0.0.1'
port = 8888
print('Using local host with IP '+ serverIp +'\nPort ' + str(port) + ' is being used')
# It's a proxy so it should problem run for every so the exit is going to be simple
print('Press crtl + c to exit out of the program\n')
# The proxy server is listening at 8888 and using a TCP socket
tcpSerSock = socket(AF_INET, SOCK_STREAM)
#Does not let it block
tcpSerSock.setblocking(0)
#Checks to see if the port is busy
try:
    tcpSerSock.bind((serverIp, port))
    isConnected = True
except:
    print('Port ' + str(port) + ' is busy')
    exit()
tcpSerSock.listen(100)
# Adds server to allow it to allows be connected to
inputs = [tcpSerSock]
outputs = []
# Dict that holds the socket message pair
clientRequestDic = {}

while 1:
    # Start receiving data from the client
    print('Ready to serve...\nCurrent inputs')
    print(inputs)
    print('\n')
    
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    # For loop for the readable list
    for s in readable:
        # print('Reading')
        if s is tcpSerSock:
            print('Server looking for a request')
            # Starting the client TCP socket
            clientSocket, addr = tcpSerSock.accept()
            # Does not let it block
            clientSocket.setblocking(0)
            # Adds to the input
            inputs.append(clientSocket)
            # Adds the new socket to the dict with an empty list that acts a queue
            clientRequestDic.update({clientSocket:[]})
            print('Received a connection from:', addr)
        else:
            # Takes the incoming message from the new socket
            print("Incoming message from "+str(s))
            message = s.recv(4096)
            # if message has something then handle that
            if message:
                #This block of code takes the list from the dict and adds the get message info
                storedClientList = clientRequestDic.get(s)
                storedClientList.append(message)
                clientRequestDic[s] = storedClientList
                # Adds the socket to the output list to show that it has something to output
                if s not in outputs:
                    outputs.append(s)
            else:
                # message is empty so need to look in the output and remove
                # then rmove from inputs, close, and delete from dict
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del clientRequestDic[s]
    
    # For loop for the writable list                                   
    for s in writable:
        # Checks to see if the socket has any messages pending
        if s in clientRequestDic.keys():
            print('Completing request for ' + str(s) + '\n')
            storedClientList = clientRequestDic.get(s)
            #Used to catch runaway sockets and checks that a message is there
            if len(storedClientList) <= 0:
                # Removes that entry from the dict and removes from both list
                inputs.remove(s)
                outputs.remove(s)
                del clientRequestDic[s]
                break
            # Pulls the info of the info from the dict
            messageLow = storedClientList[0]
            storedClientList = storedClientList[1:]
            # pulls off and removes. acts like queue
            clientRequestDic[s] = storedClientList
            
            s.sendall(messageLow.upper())
            print('Message has been sent to client\n')
            # Adds the message from web server to the cache
        else:
            # if the client has no messages then remove from outputs
            if s in outputs:
                print("removing")
                outputs.remove(s)
                print(s)
        
    # for loop used for the exceptional list
    for s in exceptional:
        # removes from inputs
        inputs.remove(s)
        # if in output remove
        if s in outputs:
            outputs.remove(s)
        # closes the socket and removes from the message dict
        s.close()
        del clientRequestDic[s]

# Close the client and the server sockets
tcpSerSock.close()