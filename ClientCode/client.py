import socket
import sys
import threading
import queue
import pickle
# import PySimpleGUI as sg
# Messages for Gil
# I think we need to look into using something like json for file transfer
# The reason for this is becase the basic sockets can only send bytes and with json it would make the format much easier
# the pickels should be fine but I'll test later
#
# The client currently sends a single image and the receiver client will get that message and write it out
# This has yet to be tested but will be.


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
        client_socket, addr = tcp_server_socket.accept()
        message = client_socket.recv(50000)
        message_queue.put(message)

def initial_message(server_socket):
    # Have to use bytes but is of form hostname, ip
    to_be_sent = hostname + ', ' + ip
    server_socket.sendall(to_be_sent.encode('utf-8'))

def get_client_list_from_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server_ip,server_port))
    server_socket.sendall(b'sendlist')
    sendable_client_list = b''
    
    message = server_socket.recv(4096)
    if not message:
        return
    else:
        sendable_client_list += message
    # Unpickle the data
    sendable_client_list = [sendable_client_list]
    return sendable_client_list

def view_and_send_clients():
    client_list = get_client_list_from_server()
    for client in client_list:
        print(client)
    client_selection = input('Enter the IP of the host you would like to send to\n>> ')
    
    test_file_name = 'fightstick.png'
    print('Message to be sent is ' + test_file_name)
    with open(test_file_name, 'rb') as imagefile:
        imagedata = imagefile.read()
    
    try:
        # Sends the image to the client
        # image needs the filename and file ext put in the message somewhere
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_selection,client_to_client_port))
        client_socket.sendall(imagedata)
        # Sends a history message to the server
        history_message = hostname + ', ' + ip + ', ' + test_file_name
        server_socket.sendall(history_message.encode('utf-8'))
        client_socket.close()
    except socket.error as e:
        print('Not a correct IP')
        
def get_message():        
    if not message_queue.empty():
        message = message_queue.get()
        return message
    else:
        return None
        
def view_messages():
    message = get_message()
    if message == None:
        print('No messages have been sent to you')
        return
    with open('test-file-send', 'wb') as imagefile:
        imagefile.write(message)
        
def view_history():
    server_socket.sendall(b'sendhistory')
    history_list = server_socket.recv(50000)
    history_list = pickle.loads(history_list)
    
    for hist in history_list:
        print(hist)

def main():
    while True:
        
        user_input = input('User menu (Enter exit to end)\n1-View and send to clients:\n2-View Messages\n3-View History\n>> ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8888))
                    
        match user_input:
            case '1': view_and_send_clients()
            case '2': view_messages()
            case '3': view_history()
            case 'exit': sys.exit()
            case _: print('Incorrect input')

        
        sock.send(user_input.encode()) 
        dataServer = sock.recv(100)
        print("Message from server: " + dataServer.decode())

if __name__ == '__main__':    
    server_ip = '127.0.0.1'
    server_port = 8888
    hostname = 'client1'
    message_queue = queue.Queue()
    
    ip = socket.gethostbyname(socket.gethostname())
    client_to_client_port = 8080
    
    
    
    #Starts the client server
    server_socket = make_server_socket(server_ip, server_port)

    # sends info to the server
    initial_message(server_socket)
    
    # Sends the initial message to the server to get the client list
    sendable_client_list = get_client_list_from_server()
    
    # starts the rec thread
    print('Receiver Thread Started\n')
    thread_rec = threading.Thread(target=client_to_client_thread, args=(client_to_client_port, ))
    thread_rec.daemon = True
    thread_rec.start()
    
    main()