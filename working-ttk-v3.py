import tkinter as tk
from tkinter import filedialog
from ttkbootstrap import *
from ttkbootstrap.constants import *
import ttkbootstrap as ttk 
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
        
###########################################

def send_to_server(server_ip, port, message_to_server):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((server_ip,int(port)))
        tcp_socket.sendall(message_to_server.encode('utf-8'))
        incoming = tcp_socket.recv(10000)
        tcp_socket.close()
        return incoming
    except socket.error as e:
        print('Incorrect ip or port server information')
        sys.exit(2)

def initial_message():
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

def send_clients(file_selection, host_name, client_list):
    # client_list = get_client_list_from_server()
    # file_selection = 'monkey.jpg'
    with open(file_selection, 'rb') as imagefile:
        imagedata = imagefile.read()
        
    try:
        # Sends the image to the client
        # image needs the filename and file ext put in the message somewhere
        tokens = file_selection.split('.')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_selection = ''
        for client in client_list:
            if client[0] == host_name:
                client_selection = client[1]
                break
        client_socket.connect((client_selection,client_to_client_port))
        
        file_message = b'name-type:' + tokens[0].encode('utf-8') + b'.' + tokens[1].encode('utf-8') + b':data:' + imagedata
        
        packets = get_packets(file_message)
        
        for packet in packets:
            client_socket.sendall(packet)
            
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

def view_history():
    incoming = send_to_server(server_ip, server_port, 'sendhistory')
    history_list = pickle.loads(incoming)
    return history_list

def leave_and_kill():
    leave_message = 'sendleave:'+ hostname + ':' + ip
    incoming = send_to_server(server_ip, server_port, leave_message)
    if incoming == b"DONE":
        sys.exit()

def submit():
    global input_hostname
    global comobox
    global input_file_name
    global client_list_server
    
    input_hostname = comobox.get()
    print('Selected host ' + input_hostname)
    print('Selected file ' + input_file_name)
    send_clients(input_file_name, input_hostname, client_list_server)

def file_exp():
    global input_file_name
    input_file_name = filedialog.askopenfilename(initialdir = "/",
                                                title = "Select a File",
                                                filetypes = (("Sendable Files"," *.png *.jpg *.gif *.jpeg *.mp4"), ("all files","*.*")))

def combobox_selected(event):
    # Get the index of the selected item
    index = event.widget.current()

    # Get the value of the selected item
    input_hostname = event.widget.get()
    
def pop_view_history():
    top_frame = ttk.Toplevel()
    top_frame.wm_title("History")
    
    history_list = view_history()
    
    label = ttk.Label(top_frame, text="History",font=("Arial", 20))
    label.grid(row=0, column=0)
        
    for i in range(len(history_list)):
        table = ttk.Entry(top_frame, width=150)
        table.grid(row=i+1, column=0)
        table.insert(ttk.END, history_list[i])

def popup_client():
    global input_hostname
    global comobox
    global client_list_server
    
    top_frame = ttk.Toplevel()
    top_frame.wm_title("Client List")
    
    client_list_server = get_client_list_from_server()
    client_list = [('Hostname', 'IP address')]
    client_drop = []
    for client in client_list_server:
        if client[1] != ip:
            client_list.append(client)
            client_drop.append(client[0])
    
    label = ttk.Label(top_frame, text="Sendable List")
    label.grid(row=0, column=0)
    
    close = ttk.Button(top_frame, text="exit", command=top_frame.destroy)
    close.grid(row=0, column=1, padx = 5, pady = 5, sticky = 'e')
    
    for i in range(len(client_list)):
        for j in range(2):
            table = ttk.Entry(top_frame, width=20)
            table.grid(row=i+1, column=j)
            table.insert(ttk.END, client_list[i][j])
            
    input_title = ttk.Label(top_frame, text="Select a Hostname")
    input_title.grid(row=4, column=0)
    
    comobox = ttk.Combobox(top_frame, state="readonly", values=client_drop)
    if len(client_drop) > 0:
        comobox.set(client_drop[0])
    comobox.grid(row=5, column=0)
    
    button_file = ttk.Button(top_frame, text="Select Image/Video", command=file_exp)
    button_file.grid(row=5, column=1, padx = 5, pady = 5)
    
    close = ttk.Button(top_frame, text="Submit", command=submit)
    close.grid(row=6, column=1, padx = 5, pady = 5)

def pop_set_name():
    top_frame = ttk.Toplevel()
    top_frame.wm_title("Set Client Name")
    top_frame.wm_geometry("600x500")

    label = ttk.Label(top_frame, text="Set Client Name", font = ("Helvetica", 18))
    label.grid(row=0, column=0,padx = 5, pady = 5)
    
    close = ttk.Button(top_frame, text="exit", command=top_frame.destroy)
    close.grid(row=0, column=1, rowspan= 1, padx = 5, pady = 5, sticky = 'e')
    
    label = ttk.Label(top_frame, text= f"Current Name: {input_hostname}", font = ("Helvetica", 18))
    label.grid(row=1, column=0)
    
    input_title = ttk.Label(top_frame, text="Enter Client Name", font = ("Helvetica", 18))
    input_title.grid(row = 2, column=0)
    
    input_field = tk.Entry(top_frame, textvariable = input_hostname)
    input_field.grid(row=3, column=0)
    
    submit = ttk.Button(top_frame, text="Submit")
    submit.grid(row=3, column=1)
    
def exit():
    leave_and_kill()

class MyApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        # Style
        self.style = ttk.Style()
        self.style.configure('my.TButton', font = ("Helvetica", 18), width = 20, height = 4)
        self.style.configure('Custom.TFrame')
        app_frame = ttk.Frame(root, style = 'Custom.TFrame')
        app_frame.pack(fill=ttk.BOTH, expand=True)

        self.label = ttk.Label(self, text="Welcome to NIVD-DC", font = ("Lato", 24))
        self.label.pack(padx= 5, pady= 5)

        self.label_frame1 = ttk.Labelframe(self, text = "Client List", bootstyle = "white")
        self.label_frame1.pack(padx=5, pady=5, fill=ttk.BOTH, expand=True)

        self.button = ttk.Button(self.label_frame1, text="Send Message to Client", command=self.popup_send, style = 'my.TButton')
        self.button.pack(padx= 5, pady= 5)
        
        self.label_frame3 = ttk.Labelframe(self, text = "View Your History", bootstyle = "white")
        self.label_frame3.pack(padx=5, pady=5, fill=ttk.BOTH, expand=True)
        self.button = ttk.Button(self.label_frame3, text="View History", command=self.popup_view_hist, style = "my.TButton")
        self.button.pack(padx= 5, pady= 5)
        
        self.label_frame4 = ttk.Labelframe(self, text = "Set Your Name", bootstyle = "white")
        self.label_frame4.pack(padx=5, pady=5, fill=ttk.BOTH, expand=True)
        self.button = ttk.Button(self.label_frame4, text="Set Client Name", command=self.popup_set_name, style = "my.TButton")
        self.button.pack(padx= 5, pady= 5)
        
        self.label_frame2 = ttk.Labelframe(self, text = "Exit the Program", bootstyle = "white")
        self.label_frame2.pack(padx=5, pady=5, fill=ttk.BOTH, expand=True)
        self.button = ttk.Button(self.label_frame2, text="Quit the Program", command=self.menu_exit, style = 'my.TButton')
        self.button.pack(padx= 5, pady= 5)
        
    def popup_send(self):
        popup_client()
        
    def test_send(self):
        send_clients()
    
    def popup_view_hist(self):
        pop_view_history()
    
    def popup_set_name(self):
        pop_set_name()
        
    def menu_exit(self):
        exit()

# Root for tk #
root = ttk.Window(themename = 'superhero')
root.title('Networks Project')
root.geometry('1000x600')
input_hostname = ''
input_file_name = ''
comobox = ttk.Combobox()
###############

client_list_server = []

server_ip = '172.17.0.4'
server_port = 8888
hostname = 'client1'

ip = socket.gethostbyname(socket.gethostname())
print(ip)

# Port used to talk between clients.
client_to_client_port = 8080

# Gets the current clients IP.
ip = socket.gethostbyname(socket.gethostname())

# Tells the server about the client
initial_message()

# Starts the client to client thread
thread_rec = threading.Thread(target=client_to_client_thread, args=(client_to_client_port, ))
thread_rec.daemon = True
thread_rec.start()

app = MyApp(root)
root.mainloop()
