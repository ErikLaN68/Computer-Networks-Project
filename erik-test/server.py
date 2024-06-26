#-------------------------------------------------------------------------------------------------
#Task List. [NEW VM Version.]
    #Normal file seems to work so adding things to make it nicer.
#1. Want Server to upkeep a list of clients. [DONE, see clients_list.txt]
#2. Need Server to handle certian messages.
    #'sendlist' [Still unfinished, must make it run on 2 machines instead of the same one].
        #Clients will send "Send me client list message." 
        #Server will Send client list!
            #Hope to use a pickled list, use the addresses.
    #'sendshutdown' [Last step, not priority yet]
    #Client will send "shutdown message"
    #Server will remove from list.
    #'sendhistory'
    #Client will send "get history message"
    #Server will send the history log.
#3. Want server to upkeep "store" of images.
    #Everytime a client sends to someone, we will append to a list!!
    #not actually a store but more like a list that contains IP addresses and names.
    #This history is to "keep security", but not actually show pictures for privacy.
        #we hope to use a tuple.
#-------------------------------------------------------------------------------------------------
#Networks Project - Server Side.
#Done By Erik L. & Gilbert G.
#-------------------------------------------------------------------------------------------------
#Default Imports.
from socket import *
import sys, select, os, time
import pickle

#IP of local host
#TODO: Add user input for changing server IP when UI is more developed.
serverIp = '127.0.0.1'
#TODO: Add GUI change to port when UI is more developed.
#Harcoded port for 8888.
port = 8888

#Print what Server IP and port are in use.
print('Using local host with IP '+ serverIp +'\nPort ' + str(port) + ' is being used')
#It's a proxy so it should problem run for every so the exit is going to be simple.
print('Press crtl + c to exit out of the program\n')
#The proxy server is listening at 8888 and using a TCP socket.
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

#This is the list of Clients. We Need to Maintain this here for server!
clients = []

#Function. Adds the ability to write the serialized clients to a .txt file.
    #It is already pickled and will persist between server uses.
def write_clients_to_file(serialized_clients, file_name):
    with open(file_name, 'w') as file:
        for client in serialized_clients:
            file.write(f"{client}\\n")

#Create function to create a history file.
#Base it off off the file sent by client (filename) and the client's IP.
#Not added yet, need to get on multiple machines.

outputs = []
address = []
# Dict that holds the socket message pair
clientRequestDic = {}
   
while 1:
    # Start receiving data from the client
    print('Ready to serve...\nCurrent inputs')
    print(clients)

    # Serialize the list
    serialized_clients = pickle.dumps(clients)
    print('\n')

    #Call write_clients_to_file the clients list to "clients_list.txt"
    write_clients_to_file(serialized_clients, "clients_list.txt")

    # Print message.
    print("The list of clients has been successfully written to clients_list.txt")
    
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    # For loop for the readable list
    for s in readable:
        if s is tcpSerSock:
            print('Server looking for a request')
            # Starting the client TCP socket
            clientSocket, addr = tcpSerSock.accept()
            # Does not let it block
            clientSocket.setblocking(0)
            # Adds to the input
            inputs.append(clientSocket)
            clients.append(addr[0])
            # Adds the new socket to the dict with an empty list that acts a queue
            clientRequestDic.update({clientSocket:[]})
            print('Received a connection from:', addr)
        else:
            # Takes the incoming message from the new socket
            print("Incoming message from "+ str(s))
            message = s.recv(50000)
            # if message has something then handle that
            if message:
                #This block of code takes the list from the dict and adds the get message info
                storedClientList = clientRequestDic.get(s)
                storedClientList.append(message)
                clientRequestDic[s] = storedClientList
                # Adds the socket to the output list to show that it has something to output
                if s not in outputs:
                    outputs.append(s)
                print('Got Message')

            #else if message is a special request from client.
            #elif message == "sendlist":
                #Get the list of clients we have already created.
                #.txt, temporarily for now.
                #with open('clients_list.txt', 'rb') as file:
                    #Read the pickled client_list.
                    #client_content = file.read()
                    #Now read, send it to the client.
                        #NOTICE: THE CLIENT MUST BE ABLE TO UNPACK IT TOO.
                    #SEND IT HERE VIA THE SOCKET.

            #else if message is special request from client.
            #elif message == "sendhistory":
                #get the history file we have created.
                #.txt temporarily.
                #with open('client_history.txt', 'rb') as file:
                    #read the history file.
                    #history_client = file.read()
                    #Now that its read, send it to client.
                        #NOTICE. CLIENT MUST BE ABLE TO DO SOMETHING WITH THIS SEND.
                    #SEND IT HERE VIA THE SOCKET.
            
            #else if message is a special request from client.
            #elif message == "sendshutdown":
                #IMPLEMENT LOGIC TO STRIKE THE CLIENT THAT SENT THIS FROM THE CLIENT LIST.

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
    
    # exception to remove cleints, probably not used.
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