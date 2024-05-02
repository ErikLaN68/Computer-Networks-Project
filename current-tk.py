import tkinter as tk
from tkinter import ttk
import socket
import sys
import threading
import queue
import pickle
import time
import subprocess
import platform

### Thread that controls client to client ###

def client_to_client_thread(client_to_client_port):
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        # will need to be the machine IP in the future
        tcp_server_socket.bind((ip, client_to_client_port))  # Start listening!
    except socket.error as e:
        print('Port is busy at the moment.\nTry again later')
        sys.exit(2)
    tcp_server_socket.listen(10)  # 10 is the max number of queued connections allowed
    currentChunk = b''
    cout = 0
    while True:
        client_socket, addr = tcp_server_socket.accept()
        get_client_message(client_socket)
        
def get_client_message(client_socket):
    currentChunk = b''
    cout = 0
    while True:
        cout = cout + 1
        message = client_socket.recv(50000)
        if cout == 44:
            return
        if message == b'':
            # message_queue.put(currentChunk)
            incoming_message_parse(currentChunk)
            currentChunk = b''
            return
        currentChunk = currentChunk + message
        
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
    file_name = tokens[1].decode()
    file_data = tokens[3]
    
    with open(file_name, 'wb') as imagefile:
        imagefile.write(file_data)
    
    if '.mp4' in file_name:
        subprocess.run('mplayer ' + file_name + ' &', shell=True)  # Opens in default application on Linux
    else:
        subprocess.run('feh ' + file_name + ' &', shell=True)  # Opens in default application on Linux
    # return tokens[1].decode(), tokens[3]
        
###########################################

def view_and_send_clients():
    # client_list = get_client_list_from_server()
    file_selection = 'monkey.jpg'
    with open(file_selection, 'rb') as imagefile:
        imagedata = imagefile.read()
        
    try:
        # Sends the image to the client
        # image needs the filename and file ext put in the message somewhere
        tokens = file_selection.split('.')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_selection = '172.17.0.3'
        client_socket.connect((client_selection,client_to_client_port))
        
        file_message = b'name-type:' + tokens[0].encode('utf-8') + b'.' + tokens[1].encode('utf-8') + b':data:' + imagedata
        
        packets = get_packets(file_message)
        
        for packet in packets:
            client_socket.sendall(packet)
            
        # Sends a history message to the server
        # history_message = 'updatehistory:' + hostname + ' with ' + ip + ' sent the file ' + tokens[0] + '.' + tokens[1] + ' to  ip ' + client_selection
        # incoming = send_to_server(server_ip, server_port, history_message)
        # if incoming == b"DONE":
        #     print('history has been sent')
        client_socket.close()
        return
    except socket.error as e:
        print('Not a correct IP or other host is not running\n')
        return
        
def get_packets(data):
    chunks = []
    currentChunk = bytearray()

    for byte in data:
        if len(currentChunk) < 10000:
            currentChunk.append(byte)
        else:
            chunks.append(currentChunk)
            currentChunk = bytearray()
            currentChunk.append(byte)
            
    chunks.append(currentChunk)
    return chunks

def popup_bonus():
    top_frame = tk.Toplevel()
    top_frame.wm_title("Client List")
    
    test = [('Hostname', 'IP address'), ('client1', 123), ('client2', 456)]
    
    label = tk.Label(top_frame, text="Sendable List")
    label.grid(row=0, column=0)
    
    close = tk.Button(top_frame, text="exit", command=top_frame.destroy)
    close.grid(row=0, column=1)
    
    for i in range(3):
        for j in range(2):
            # font=('Arial',16,'bold')
            table = tk.Entry(top_frame, width=20)
            table.grid(row=i+1, column=j)
            table.insert(tk.END, test[i][j])
            
    input_title = tk.Label(top_frame, text="Enter Hostname")
    input_title.grid(row=4, column=0)
    
    input_field = tk.Entry(top_frame, textvariable = input_hostname)
    input_field.grid(row=5, column=0)
    
    close = tk.Button(top_frame, text="Submit", command=top_frame.destroy)
    close.grid(row=5, column=1)

class MyApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        
        app_frame = tk.Frame(root, width=400, height=400)
        app_frame.pack(fill=tk.BOTH, expand=True)
        
        self.label = tk.Label(self, text="Welcome the Image/Video Sender, Reciver and viewer")
        self.label.pack()

        self.button = tk.Button(self, text="Send Message to Client", command=self.popup)
        self.button.pack()
        
        self.button = tk.Button(self, text="view files", command=self.file_exp)
        self.button.pack()
        
        self.button = tk.Button(self, text="test send", command=self.test_send)
        self.button.pack()
        
        self.button = tk.Button(self, text="View History", command=self.on_click)
        self.button.pack()
        
        self.button = tk.Button(self, text="Set Client Name", command=self.on_click)
        self.button.pack()

    def on_click(self):
        self.label.config(text="You clicked the button!", command=subprocess.run('feh monkey.jpg &', shell=True))
        
    def file_exp(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Sendable Files"," *.png *.jpg *.gif *.jpeg *.mp4"), ("all files","*.*")))
        
    def popup(self):
        popup_bonus()
        
    def test_send(self):
        view_and_send_clients()

    def send_to_server(self, server_ip, port, message_to_server):
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
    
    # def view_and_send_clients(self):
    #     # client_list = get_client_list_from_server()
                
    #     with open('monkey.jpg', 'rb') as imagefile:
    #         imagedata = imagefile.read()
            
    #     try:
    #         # Sends the image to the client
    #         # image needs the filename and file ext put in the message somewhere
    #         tokens = file_selection.split('.')
    #         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         client_selection = '172.17.0.3'
    #         client_socket.connect((client_selection,client_to_client_port))
            
    #         file_message = b'name-type:' + tokens[0].encode('utf-8') + b'.' + tokens[1].encode('utf-8') + b':data:' + imagedata
            
    #         packets = get_packets(file_message)
            
    #         for packet in packets:
    #             client_socket.sendall(packet)
                
    #         # Sends a history message to the server
    #         # history_message = 'updatehistory:' + hostname + ' with ' + ip + ' sent the file ' + tokens[0] + '.' + tokens[1] + ' to  ip ' + client_selection
    #         # incoming = send_to_server(server_ip, server_port, history_message)
    #         # if incoming == b"DONE":
    #         #     print('history has been sent')
    #         client_socket.close()
    #         return
    #     except socket.error as e:
    #         print('Not a correct IP or other host is not running\n')
    #         return
        
    # def get_message():        
    #     if not message_queue.empty():
    #         message = message_queue.get()
    #         return message
    #     else:
    #         return None

    # def incoming_message_parse(incoming):
    #     tokens = []
    #     col_data = False
    #     currword = bytearray()
        
    #     for byte in incoming:
    #         if len(tokens) >= 3:
    #             col_data = True
    #         if byte != ord(':'):
    #             currword.append(byte)
    #         elif col_data:
    #             currword.append(byte)
    #         elif len(tokens) < 3:
    #             tokens.append(currword)
    #             currword = bytearray()
                
    #     tokens.append(currword)
    #     return tokens[1].decode(), tokens[3]
    
    # def view_messages():
    #     message = get_message()
    #     if message == None:
    #         print('\nNo messages have been sent to you\n')
    #         return
        
    #     file_name, file_data = incoming_message_parse(message)
        
    #     with open(file_name, 'wb') as imagefile:
    #         imagefile.write(file_data)
            
    #     # Determine the operating system
    #     if platform.system() == 'Windows':
    #         subprocess.run('start /MAX test-file-send', shell=True)  # Opens in fullscreen on Windows
    #     elif platform.system() == 'Darwin':  # macOS
    #         subprocess.run('open -a Preview.app --args -F test-file-send', shell=True)  # Opens in fullscreen with Preview app
    #     elif platform.system() == 'Linux':
    #         if '.mp4' in file_name:
    #             subprocess.run('mplayer ' + file_name, shell=True)  # Opens in default application on Linux
    #         else:
    #             subprocess.run('feh ' + file_name, shell=True)  # Opens in default application on Linux
    #     return
    
    def view_history(self):
        incoming = send_to_server(server_ip, server_port, 'sendhistory')
        history_list = pickle.loads(incoming)
        
        print('\n--- Message History ---')
        for hist in history_list:
            print(hist)
        print('-----------------------\n')
    
    def leave_and_kill(self):
        leave_message = 'sendleave:'+ hostname + ':' + ip
        incoming = send_to_server(server_ip, server_port, leave_message)
        if incoming == b"DONE":
            sys.exit()

# Root for tk #
root = tk.Tk()
root.title('Networks Project')
input_hostname = tk.StringVar()
###############

server_ip = '172.17.0.3'
server_port = 8888
hostname = 'client3'
message_queue = queue.Queue()
ip = socket.gethostbyname(socket.gethostname())
print(ip)
# Port used to talk between clients.
client_to_client_port = 8080

# Gets the current clients IP.
ip = socket.gethostbyname(socket.gethostname())
print(ip)
# Port used to talk between clients.
client_to_client_port = 8080
thread_rec = threading.Thread(target=client_to_client_thread, args=(client_to_client_port, ))
thread_rec.daemon = True
thread_rec.start()
app = MyApp(root)
root.mainloop()
