import socket
import threading
import time

HEADER = 64
PORT = 5000
FORMAT = 'utf-8'
SERVER = '192.168.1.16'

def send(msg):
    message = msg.encode(FORMAT)
    # msg_length = len(message)
    # send_length = str(msg_length).encode(FORMAT)
    # send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    client.send(message)
    
    
def receive(client):
    while True:
        print(client.recv(2048).decode(FORMAT))
    
    
print("Enter your name: ")
name = input()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
send(name)
thread = threading.Thread(target=receive, args=(client,))
thread.start()

while True:
    msg = input()
    send(msg)
