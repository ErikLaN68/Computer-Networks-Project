import socket
import sys
import threading
import queue
import pickle
# import PySimpleGUI as sg


def start_server(port):
    # This function will create our TCP Server Socket, start listening, then return the Socket Object
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Blocking is set to 1 because threading is being used.
    # The main server will block and wait for a connect from many clients and then let threads do the work concurrently
    tcp_server_socket.setblocking(1)
    # Checking that the port is not being used
    try:
        tcp_server_socket.bind(('127.0.0.1', port))  # Start listening!
    except socket.error as e:
        print('Port is busy at the moment.\nTry again later')
        sys.exit(2)
    return tcp_server_socket

def make_server_socket(ip, port):
    # This function will be used to create a socket and connect to server
    # Try is used to make sure the user given infomation is correct
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ip,int(port)))
    except socket.error as e:
        print('Incorrect ip or port server information')
        sys.exit(2)
        
    print("Connected to server!\n")
    return tcp_socket

def client_to_client_thread(client_to_client_port):
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        # will need to be the machine IP in the future
        tcp_server_socket.bind(('127.0.0.1', client_to_client_port))  # Start listening!
    except socket.error as e:
        print('Port is busy at the moment.\nTry again later')
        sys.exit(2)
    tcp_server_socket.listen(10)  # 10 is the max number of queued connections allowed
    while True:
        client_socket, addr = server_socket.accept()
        message = client_socket.recv(4094)

if __name__ == '__main__':    
    server_ip = '127.0.0.1'
    server_port = 8888
    
    client_to_client_port = 8080
    #Connect to server
    server_socket = make_server_socket(server_ip, server_port)
    
    print('Receiver Thread Started\n')
    thread_rec = threading.Thread(target=client_to_client_thread, args=(client_to_client_port))
    thread_rec.daemon = True
    thread_rec.start()
    
    while True:
        
        user_input = input('User menu (Enter exit to end)\n1-View Sendable Clients:\n2-View Messages\n3-Send Message\n>> ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8888))
                    
        match user_input:
            case '1': print('hold 1')
            case '2': print('Hold 2')
            case '3': print('Hold 3')
            case 'exit': sys.exit()
            case _: print('Incorrect input')
            
            
        
        sock.send(user_input.encode()) 
        dataServer = sock.recv(100)
        print("Message from server: " + dataServer.decode())

   
    sock.close()