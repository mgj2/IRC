import socket
import threading
import os
import sys


FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '127.0.0.1'
PORT = 64444


def send(client, msg):
    # global receive_thread
    message = msg.encode(FORMAT)
    client.send(message)
    if message == '!q':
        os._exit(1)

    
def receive(client):
    while True:
        print(client.recv(2048).decode(FORMAT))


def user_naming(client):
    print("Enter your name: ")
    name = input()
    send(client, name)
    try:
        flag = client.recv(2048).decode(FORMAT)
        return flag
    except ConnectionResetError:
        print('The server is not responding and crashed, please try after sometime, disconnecting the session now')
        exit(1)
    except ConnectionRefusedError:
        print('The chat server is not available, disconnecting the session now')
        exit(1)
    

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
    except ConnectionResetError:
        print('The server is not responding and crashed, please try after sometime, disconnecting the session now')
        exit(1)
    except ConnectionRefusedError:
        print('The chat server is not available, disconnecting the session now')
        exit(1)
                
    while True:
        # calling the user_naming function to take username from user and perform naming conventions
            
        flag = user_naming(client)
        if flag != 'You are in the lobby.':
            print(flag)
                
        else:   
            # Specifies a second thread.  Loops infinitely inside receive()
            send_thread = threading.Thread(target=send, args=(client,))
            send_thread.start()
            break

    while True:
        receive(client)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)
