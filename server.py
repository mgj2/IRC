import socket
import threading
import time

HEADER = 32
PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# global message buffer
buffer = []
# list of connections in the chat room
group = []


def handle_client(conn, addr):
    global buffer
    global group
    
    # msg_length = conn.recv(1).decode(FORMAT)
    # msg_length = int(msg_length)
    name = conn.recv(1024).decode(FORMAT)
    # Prints to server console
    print(addr, " has joined as ", name)
    
    # Adds current connection to the list of current connections
    group.append((conn, addr))
    
    # Loops until connected is False (client sends '!q')
    connected = True
    while connected:
        # Receives the header containing the message size
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        
        msg = conn.recv(1024).decode(FORMAT)

        # Does not enter if statement unless a message has been received
        if not msg == '':
            # msg_length = int(msg_length)
            if msg == '!q':
                connected = False
                disc_str = addr + "has disconnected"
                print(disc_str)
                buffer.append(disc_str)
                group.remove((conn, addr))
            else:
                print(addr, ":", msg)
                new_msg = name + ": " + msg
                buffer.append(new_msg)

        # Pops the buffer and sends the messages to all clients
        while buffer:
            for i in group:
                new_msg = buffer.pop()
                i[0].send(new_msg.encode(FORMAT))
        time.sleep(1)
    conn.close()


def start():
    global buffer
    server.listen()
    print("Server address: ", SERVER)
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active Connections: ", threading.active_count()-1, "\n")


print("Starting server...")
start()
