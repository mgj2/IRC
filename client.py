import socket
import threading
import time
import os


# ExitCommand class, signal_handler() adapted from


class ExitCommand(Exception):
    pass


def signal_handler(signal, frame):
    raise ExitCommand()


FORMAT = 'utf-8'
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER= '127.0.0.1'
PORT= 64444


def send(client, msg):
    # global receive_thread
    message = msg.encode(FORMAT)
    client.send(message)
    # if message == '!q':
    #     os.kill(receive_thread.native_id, signal.SIGTERM)
    #     exit(0)

    
def receive(client):
    while True:
        print(client.recv(2048).decode(FORMAT))
        

def main():
    print("Enter your name: ")
    name = input()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    send(client, name)
    # Specifies a second thread.  Loops infinitely inside receive()
    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    while True:
        msg = input()
        send(client, msg)


if __name__ == "__main__":
    main()
