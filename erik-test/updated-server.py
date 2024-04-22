import socket
import select
import pickle

# IP address and port for the server
server_ip = socket.gethostbyname(socket.gethostname())
port = 8888

# Print server details
print('Server IP is ' + server_ip + '\nPort ' + str(port) + ' is being used')
print('Press ctrl + c to exit out of the program\n')

# Create a TCP socket
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.setblocking(0)

# Bind the socket to the server address and port
try:
    tcp_server_socket.bind((server_ip, port))
    is_connected = True
except OSError:
    print('Port ' + str(port) + ' is busy')
    exit()

# Listen for incoming connections
tcp_server_socket.listen(100)

# Lists to keep track of inputs, outputs, and clients
inputs = [tcp_server_socket]
outputs = []

#This is the list of Clients. We Need to Maintain this here!
clients = []

# Dictionary to keep track of clients and their requests
client_request_dict = {}

# Function to write the serialized clients to a file
def write_clients_to_file(serialized_clients, file_name):
    with open(file_name, 'wb') as file:
        file.write(serialized_clients)

# Main server loop
while True:
    # Start receiving data from the client
    # print('Ready to serve...\nCurrent inputs')
    # print(client_request_dict)

   # Extract the client addresses from the client sockets
    # client_addresses = [sock.getpeername()[0] for sock in client_request_dict.keys()]   

    # Serialize the list of client addresses
    serialized_clients = pickle.dumps(clients)

    # print('\n')
    # Write the serialized clients to a file
    write_clients_to_file(serialized_clients, "clients_list.txt")
    # print(serialized_clients)
    # print("The list of clients has been successfully written to clients_list.txt")

    # Use select to monitor sockets for readable, writable, or exceptional conditions
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # Handle sockets with incoming data
    for sock in readable:
        if sock is tcp_server_socket:
            print('Server looking for a request')
            # Accept incoming connection
            client_socket, addr = tcp_server_socket.accept()
            client_socket.setblocking(0)
            inputs.append(client_socket)
            # Adds the new socket to the dict with an empty list that acts a queue
            client_request_dict.update({client_socket: []})
            # print('Received a connection from:', addr)
        else:
            # Receive message from client
            print("Incoming message from " + str(sock))
            message = sock.recv(50000)
            print(message)
            if message:
                stored_client_list = client_request_dict.get(sock)
                stored_client_list.append(message)
                client_request_dict[sock] = stored_client_list
                if sock not in outputs:
                    outputs.append(sock)
                print('Got Message')       
            else:
                # Close the socket if no message is received
                if sock in outputs:
                    outputs.remove(sock)
                inputs.remove(sock)
                # sock.close()
                del client_request_dict[sock]

    # Handle sockets with pending messages to send
    for sock in writable:
        if sock in client_request_dict.keys():
            print('Completing request for ' + str(sock) + '\n')
            stored_client_list = client_request_dict.get(sock)
            if len(stored_client_list) <= 0:
                inputs.remove(sock)
                outputs.remove(sock)
                del client_request_dict[sock]
                continue
            message = stored_client_list[0]
            stored_client_list = stored_client_list[1:]
            client_request_dict[sock] = stored_client_list
            # Handle special messages from client
            if 'hello:' in message.decode('utf-8'):
                print('Printing the message')
                print(message)
                message = message.decode('utf-8')
                tokens = message.split(':')
                hostname = tokens[1]
                hostIP = tokens[2]
                pair = (hostname, hostIP)
                print(pair)
                if pair not in clients:
                    clients.append(pair)
                print(clients)
                sock.sendall(b'DONE')
            elif message == b'sendlist':
                # Send the serialized client list to the client
                sock.sendall(serialized_clients)
            elif message == b'sendhistory':
                # Send the a list of messages the client has received
                sock.sendall(pickle.dumps(stored_client_list))
            elif message == b'sendleave':
                # Remove client from the list
                del client_request_dict[sock]
                inputs.remove(sock)
                outputs.remove(sock)
                print('Client ' + str(sock) + ' removed.')
            print('Message has been sent to client\n')
        else:
            if sock in outputs:
                print("removing")
                outputs.remove(sock)

    # Handle exceptional conditions
    for sock in exceptional:
        inputs.remove(sock)
        if sock in outputs:
            outputs.remove(sock)
        sock.close()
        del client_request_dict[sock]

# Close the server socket
tcp_server_socket.close()
