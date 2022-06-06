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
        try:
            client.send(message)
            if msg == '!q':
                exit(0)
        except ConnectionResetError:
            break

    
def receive(client, send_thread) -> int:
    while True:
        try:
            resp = client.recv(2048).decode(FORMAT)
            if resp == 'quit':
                return 0
            else:
                print(resp)
        except ConnectionResetError:
            print("Server not responding.  Exiting...")
            return 1


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

    try:
        exit_code = receive(client, send_thread)
        send_thread.join()
        exit(exit_code)
    except KeyboardInterrupt:
        print("Interrupted")
        send_thread.join()
        client.close()
        exit(1)


if __name__ == "__main__":
    main()
