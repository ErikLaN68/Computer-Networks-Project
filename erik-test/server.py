#Need this to upkeep a list of clients.
#Need this to handle certian messages.
    #Clients will send "Send me cleient message"
    #send a message that says shutdown to remove from list.

#have an image recieved. Server will keep a history.
#Have a peered history? Log?

#HAVE GIL ADD TO SERVER:
#Add the maintaining of a list
#Be able to send list back to clients using serialized messages.
#Make a store of pictures (Actually ip address and name)

#TUPLE FUCK CONCAT STRING

#Standardzed message format
#The client will send 'sendlist'
#The server will then send the list of other clients.

#Everytime a client sends to someone, we will append to a list
#that contain the ip addresses and name.
#The client can request to see this list via a message named 'sendhistory'


#Networks Assignment - Server Select

from socket import *
import sys, select, os, time
import pickle

#IP of local host
#Add user input for changing server IP later.
serverIp = '127.0.0.1'
#Add GUI change to port later.
port = 8888

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

#This is the list of Clients. We Need to Maintain this here!
clients = []

#Function. Adds the ability to write the serialized clients to a .txt file.
    #It is already pickled and will persist between server uses.
def write_clients_to_file(serialized_clients, file_name):
    with open(file_name, 'w') as file:
        for client in serialized_clients:
            file.write(f"{client}\\n")

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
            print("Incoming message from "+str(s))
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