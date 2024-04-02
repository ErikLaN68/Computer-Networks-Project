import socket

import socket

print('Enter exit to quite')
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('172.17.0.3', 8888))
    inputData = input("Please enter: ")
    if inputData == "exit":
        sock.close()
        break
    sock.send(inputData.encode()) 
    dataServer = sock.recv(100)
    print("Message from server: " + dataServer.decode())
    sock.close()
        
