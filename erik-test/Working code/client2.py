import socket
import sys
import threading
import queue
import pickle
import time
import subprocess
import platform

# Client1

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

def send_to_server(server_ip, port, message_to_server):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((server_ip,int(port)))
        tcp_socket.sendall(message_to_server.encode('utf-8'))
        incoming = tcp_socket.recv(1024)
        tcp_socket.close()
        return incoming
    except socket.error as e:
        print('Incorrect ip or port server information')
        sys.exit(2)

def client_to_client_thread(client_to_client_port):
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        # will need to be the machine IP in the future
        tcp_server_socket.bind((ip, client_to_client_port))  # Start listening!
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
    to_be_sent = 'hello:'+ hostname + ':' + ip
    incoming = send_to_server(server_ip, server_port, to_be_sent)
    if incoming == b"DONE":
        return

def get_client_list_from_server():
    incoming = send_to_server(server_ip, server_port, 'sendlist')
    sendable_client_list = b''
    # message = server_socket.recv(4096)
    if not incoming:
        return
    else:
        sendable_client_list = incoming
    # Unpickle the data
    sendable_client_list = pickle.loads(sendable_client_list)
    return sendable_client_list

def view_and_send_clients():
    client_list = get_client_list_from_server()
    if len(client_list) > 1:
        print('\n--- Sendable Clients ---')
        for client in client_list:
            if client[1] != ip:
                print('| Hostname: ' + client[0] + ' | IP: ' + client[1] + ' |')
        print('------------------------\n')
    else:
        print('\nYou are the only user at this time\n')
        return
    
    client_selection = input('Enter the IP of the host you would like to send to (type exit to quit)\n>> ')
    if client_selection.lower() == 'exit':
        return
    
    search = subprocess.run("ls | grep -E '\.jpg$|\.jpeg$|\.png$|\.gif$|\.mp4$'", shell=True, capture_output=True, text=True)
    
    print("\n--- Image and Video Files that can be sent to another machine in current directory ---\n")
    print(search.stdout)
    print("---------------------------------------------------------------------------------------\n")
    
    file_selection = input('Enter the relative path for files in the current directory or give full path for files outside of directory\n>> ')

    print('\nPicked file is ' + file_selection)
    
    with open(file_selection, 'rb') as imagefile:
        imagedata = imagefile.read()
        
    try:
        # Sends the image to the client
        # image needs the filename and file ext put in the message somewhere
        tokens = file_selection.split('.')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_selection,client_to_client_port))
        file_message = b'name:' + tokens[0].encode('utf-8') + b'filetype:' + tokens[1].encode('utf-8') + b'data:' + imagedata
        client_socket.sendall(file_message)
        # Sends a history message to the server
        history_message = 'updatehistory:' + hostname + ' with ' + ip + ' sent the file ' + tokens[0] + '.' + tokens[1] + ' to  ip ' + client_selection
        incoming = send_to_server(server_ip, server_port, history_message)
        if incoming == b"DONE":
            print('history has been sent')
        client_socket.close()
        return
    except socket.error as e:
        print('Not a correct IP or other host is not running\n')
        return
        
def get_message():        
    if not message_queue.empty():
        message = message_queue.get()
        return message
    else:
        return None

def incoming_message_parse(incoming):
    tokens = []
    col_data = False
    currword = bytearray()
    
    for byte in incoming:
        if len(tokens) >= 3:
            col_data = True
        if byte != ord(':'):
            currword.append(byte)
        elif col_data:
            currword.append(byte)
        elif len(tokens) < 3:
            tokens.append(currword)
            currword = bytearray()
            
    tokens.append(currword)
    print(tokens)
    print(len(tokens))
    print(tokens[1].decode())
    return tokens[1].decode(), tokens[3]
        

def view_messages():
    message = get_message()
    if message == None:
        print('\nNo messages have been sent to you\n')
        return
    
    file_name, file_data = incoming_message_parse(message)
    
    with open(file_name, 'wb') as imagefile:
        imagefile.write(file_data)
        
    # Determine the operating system
    if platform.system() == 'Windows':
        subprocess.run('start /MAX test-file-send', shell=True)  # Opens in fullscreen on Windows
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run('open -a Preview.app --args -F test-file-send', shell=True)  # Opens in fullscreen with Preview app
    elif platform.system() == 'Linux':
        subprocess.run('feh ' + file_name, shell=True)  # Opens in default application on Linux
        
    return
        
def view_history():
    incoming = send_to_server(server_ip, server_port, 'sendhistory')
    history_list = pickle.loads(incoming)
    
    print('\n--- Message History ---')
    for hist in history_list:
        print(hist)
    print('-----------------------\n')

def leave_and_kill():
    leave_message = 'sendleave:'+ hostname + ':' + ip
    incoming = send_to_server(server_ip, server_port, leave_message)
    if incoming == b"DONE":
        sys.exit()

def main():
    while True:
        
        user_input = input('User menu (Enter exit to end)\n1-View and send to clients:\n2-View Messages\n3-View History\n>> ')

        match user_input:
            case '1': view_and_send_clients()
            case '2': view_messages()
            case '3': view_history()
            case 'exit': leave_and_kill()
            case _: print('Incorrect input')

if __name__ == '__main__':    
    server_ip = '172.17.0.2'
    server_port = 8888
    hostname = 'client1'
    message_queue = queue.Queue()
    
    # Gets the current clients IP.
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    # Port used to talk between clients.
    client_to_client_port = 8080
    
    
    
    #Starts the client server
    # server_socket = make_server_socket(server_ip, server_port)

    # sends info to the server
    initial_message(None)
    print('Send start message')
    print('Between')
    # Sends the initial message to the server to get the client list
    sendable_client_list = get_client_list_from_server()
    print('Sending request for list')
    # starts the rec thread
    print('Receiver Thread Started\n')
    thread_rec = threading.Thread(target=client_to_client_thread, args=(client_to_client_port, ))
    thread_rec.daemon = True
    thread_rec.start()
    
    main()