import socket
import threading
import signal


FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 64444
send_thread = None


def graceful_exit(signal_received, frame):
    print("Interrupted")
    if send_thread:
        send_thread.join()
    exit(1)


signal.signal(signal.SIGINT, graceful_exit)


def send(client):
    while True:
        try:
            msg = input()
            print('.')
            message = msg.encode(FORMAT)
        except (EOFError, KeyboardInterrupt):
            "Interrupted"
            break
        try:
            client.send(message)
            if msg == '!q':
                exit(0)
        except ConnectionResetError:
            break

    
def receive(client) -> int:
    while True:
        try:
            resp = client.recv(2048).decode(FORMAT)
            if resp == 'quit':
                return 0
            else:
                print(resp)
        except TimeoutError:
            pass
        except ConnectionResetError:
            print("Server not responding.  Exiting...")
            return 1
        except KeyboardInterrupt:
            print("interrupted")
            return 1


def user_naming(client):
    print("Enter your name: ")
    name = input()
    client.send(name.encode(FORMAT))
    flag = client.recv(2048).decode(FORMAT)
    return flag


def main():
    global send_thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(.2)
    except (ConnectionError, ConnectionRefusedError) as e:
        print(e)
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

    try:
        exit_code = receive(client)
        send_thread.join()
        exit(exit_code)
    except KeyboardInterrupt:
        print("Interrupted")
        send_thread.join()
        client.close()
        exit(1)


if __name__ == "__main__":
    main()
