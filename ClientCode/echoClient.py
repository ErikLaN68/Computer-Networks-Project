import socket

with open('fightstick.png', 'rb') as imagefile:
    imagedata = imagefile.read()

print('Enter exit to quite')
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8880))
    inputData = input("Please enter: ")
    if inputData == "exit":
        sock.close()
        break
    sock.sendall(imagedata) 
    dataServer = sock.recv(50000)
    print("Message from server: " + dataServer.decode())
sock.close()
        
