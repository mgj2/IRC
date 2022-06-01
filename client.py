import socket
import threading
import os


FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '127.0.0.1'
PORT = 64444


def send(client):
    while True:
        msg = input()
        message = msg.encode(FORMAT)
        client.send(message)
        if msg == '!q':
            os._exit(0)

    
def receive(client):
    while True:
        print(client.recv(2048).decode(FORMAT))


def user_naming(client):
    print("Enter your name: ")
    name = input()
    client.send(name.encode(FORMAT))
    flag = client.recv(2048).decode(FORMAT)
    return flag


def main():
    # print("Enter your name: ")
    # name = input()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    # calling the user_naming function to take username from user and perform naming conventions
    flag = user_naming(client)
    if flag != 'You are in the lobby.':
        print(flag)
    else:
        # Specifies a second thread.  Loops infinitely inside receive()
        send_thread = threading.Thread(target=send, args=(client,))
        send_thread.start()

    while True:
        receive(client)


if __name__ == "__main__":
    main()
