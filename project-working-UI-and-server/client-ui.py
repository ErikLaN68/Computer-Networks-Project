import tkinter as tk
from tkinter import filedialog
from ttkbootstrap import *
from ttkbootstrap.constants import *
import ttkbootstrap as ttk 
import socket
import sys
import threading
import pickle
import subprocess
import os
import rsa
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

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
    while True:
        client_socket, addr = tcp_server_socket.accept()
        get_client_message(client_socket)
        
def get_client_message(client_socket):
    currentChunk = b''
    while True:
        message = client_socket.recv(70000)
        if message == b'':
            incoming_message_parse(currentChunk)
            currentChunk = b''
            return
        currentChunk = currentChunk + message
        
def get_key(incoming):
    found = False
    skip = False
    skip_count = 0
    file_data = ''
    key = ''
    currword = bytearray()
    for i, byte in enumerate(incoming):
        if skip_count > 3:
            skip = False 
        if byte == ord('k') and incoming[i+1] == ord('e') and incoming[i+2] == ord('y') and incoming[i+3] == ord(':') and not found:
            found = True
            file_data = currword
            currword = bytearray()
            skip = True
        if not skip:
            currword.append(byte)
        else:
            skip_count = skip_count + 1
            
    key = currword
    return key, file_data

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

    aes_key_enc, file_data = get_key(tokens[3])
        
    aes_key = rsa.decrypt(aes_key_enc, privk)
    
    iv = b'clienttoclientiv'
    aes_ob = AES.new(aes_key, AES.MODE_CFB, iv)
    
    plain_text = aes_ob.decrypt(bytes(file_data))
    
    with open(file_name, 'wb') as imagefile:
        imagefile.write(plain_text)
    
    if '.mp4' in file_name:
        subprocess.run('mplayer ' + file_name + ' &', shell=True)  # Opens in default application on Linux
    else:
        subprocess.run('feh ' + file_name + ' &', shell=True)  # Opens in default application on Linux
        
###########################################

def send_to_server(server_ip, port, message_to_server):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((server_ip,int(port)))
        if type(message_to_server) == bytes:
            tcp_socket.sendall(message_to_server)
        else:
            tcp_socket.sendall(message_to_server.encode('utf-8'))
        incoming = tcp_socket.recv(10000)
        tcp_socket.close()
        return incoming
    except socket.error as e:
        print('Incorrect ip or port server information')
        sys.exit(2)

def initial_message():
    # Have to use bytes but is of form hostname, ip
    to_be_sent = b'hello:' + hostname.encode('utf-8') + b':' + ip.encode('utf-8') + b':' + pickle.dumps(pubk)
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
    if file_selection == '' or type(file_selection) == tuple:
        tk.messagebox.showerror('test','Please Select a file')
        return
    
    with open(file_selection, 'rb') as imagefile:
        imagedata = imagefile.read()
    
    client_selection = ''
    client_pub_key = ''
    for client in client_list:
        if client[0] == host_name:
            client_selection = client[1]
            client_pub_key = client[2]
            break
        
    client_pub_key = pickle.loads(client_pub_key)
    
    aes_key = get_random_bytes(16)
    iv = b'clienttoclientiv'
    
    rsa_enc_key = rsa.encrypt(aes_key, client_pub_key)
    
    aes_ob = AES.new(aes_key, AES.MODE_CFB, iv)
    cipher_text = aes_ob.encrypt(imagedata)
    
    try:
        # Sends the image to the client
        # image needs the filename and file ext put in the message somewhere
        tokens = file_selection.split('/')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_selection,client_to_client_port))
        file_message = b'name-type:' + tokens[len(tokens)-1].encode('utf-8') + b':data:' + cipher_text + b'key:'+rsa_enc_key
        
        packets = get_packets(file_message)
        
        for packet in packets:
            client_socket.sendall(packet)
        
        # Sends a history message to the server
        history_message = 'updatehistory:' + hostname + ' with ' + ip + ' sent the file ' + tokens[0] + '.' + tokens[1] + ' to  host ' + host_name + ' with IP ' + client_selection
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
        if len(currentChunk) < 50000:
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

def submit_send():
    global comobox
    global input_file_name
    global client_list_server
    
    send_hostname = comobox.get()
    send_clients(input_file_name, send_hostname, client_list_server)

def submit_name():
    global input_hostname
    global hostname
    
    hostname = input_hostname.get()
    
    to_be_sent = 'updatename:' + hostname + ':' + ip
    incoming = send_to_server(server_ip, server_port, to_be_sent)
    if incoming == b"DONE":
        tk.messagebox.showinfo('Name Changed','Name has been Changed')
        return

def file_exp():
    global input_file_name
    input_file_name = filedialog.askopenfilename(initialdir = "/home/code",
                                                title = "Select a File",
                                                filetypes = (("Sendable Files"," *.png *.jpg *.gif *.jpeg *.mp4"), ("all files","*.*")))
    
def pop_view_history():
    top_frame = ttk.Toplevel()
    top_frame.wm_title("History")
    
    history_list = view_history()
    
    label = ttk.Label(top_frame, text="History",font=("Helvetica", 20))
    label.grid(row=0, column=0)
        
    for i in range(len(history_list)):
        table = ttk.Entry(top_frame, width=100)
        table.grid(row=i+1, column=0)
        table.insert(ttk.END, history_list[i])

def popup_client():
    global comobox
    global client_list_server
    
    top_frame = ttk.Toplevel()
    top_frame.wm_title("Client List")
    top_frame.attributes("-topmost", True)
    
    client_list_server = get_client_list_from_server()
    client_list = [('Hostname', 'IP address')]
    client_drop = []
    for client in client_list_server:
        if client[1] != ip:
            client_list.append(client)
            client_drop.append(client[0])
    
    label = ttk.Label(top_frame, text="Sendable Clients", font = ("Helvetica", 18))
    label.grid(row=0, column=0)
    
    close = ttk.Button(top_frame, text="exit", command=top_frame.destroy)
    close.grid(row=0, column=4, padx = 5, pady = 5, sticky = 'e')
    
    for i in range(len(client_list)):
        for j in range(2):
            table = ttk.Entry(top_frame, width=20)
            table.grid(row=i+1, column=j)
            table.insert(ttk.END, client_list[i][j])
            
    input_title = ttk.Label(top_frame, text="Select a Hostname", font = ("Helvetica", 14))
    input_title.grid(row=1, column=3, padx = 5, pady = 10)
    
    comobox = ttk.Combobox(top_frame, state="readonly", values=client_drop)
    if len(client_drop) > 0:
        comobox.set(client_drop[0])
    comobox.grid(row=2, column=3,  padx = 5, pady = 5)
    
    button_file = ttk.Button(top_frame, text="Select Image/Video", command=file_exp)
    button_file.grid(row=2, column=4, padx = 5, pady = 5)
    
    close = ttk.Button(top_frame, text="Send Message", command=submit_send)
    close.grid(row=3, column=4, padx = 5, pady = 5)

def pop_set_name():
    global input_hostname
    
    top_frame = ttk.Toplevel()
    top_frame.wm_title("Set Client Name")
    #top_frame.wm_geometry("600x500")

    label = ttk.Label(top_frame, text="Pick a New Name!", font = ("Helvetica", 18))
    label.grid(row=0, column=0,padx = 5, pady = 5)
    
    label = ttk.Label(top_frame, text= f"Current Name: {hostname}", font = ("Helvetica", 14))
    label.grid(row=1, column=0)
    
    input_title = ttk.Label(top_frame, text="Enter New Name", font = ("Helvetica", 14))
    input_title.grid(row = 2, column=0)
    
    input_field = tk.Entry(top_frame, textvariable=input_hostname)
    input_field.grid(row=3, column=0)
    
    submit = ttk.Button(top_frame, text="Change Name", command=submit_name)
    submit.grid(row=3, column=1)
    
    close = ttk.Button(top_frame, text="exit", command=top_frame.destroy)
    close.grid(row=3, column=2, rowspan= 1, padx = 5, pady = 5, sticky = 'e')
    
def exit_app():
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

        self.label = ttk.Label(self, text="Welcome to NVID-DC", font = ("Lato", 24))
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
        exit_app()

# Sets the dispaly env for the xserver
os.environ["DISPLAY"] = '192.168.56.1:0.0'

# RSA keys
(pubk, privk) = rsa.newkeys(1024)

# Root for tk #
root = ttk.Window(themename = 'superhero')
root.title('Networks Project')
root.geometry('1000x600')
input_hostname = StringVar()
input_file_name = ''
comobox = ttk.Combobox()
###############

client_list_server = []

server_ip = '172.17.0.3'
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
