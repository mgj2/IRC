import socket
import threading
import time


class User:
    def __init__(self, new_conn, new_addr, new_nick):
        self.conn = new_conn
        self.addr = new_addr
        self.nick = new_nick
        self.room = 0
        
        
class Room:
    def __init__(self):
        self.buffer = []
        self.users = []
        

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
ROOMS = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


clients = {}
# list of connections in the chat room
rooms = []


def print_welcome(room):
    print("Welcome to room", room)
    print_options()


def print_options() -> str:
    msg = "!h for help \n" + \
          "!v to view the list of rooms \n" + \
          "!c to create a room \n" + \
          "!j to join a room \n" + \
          "!l to leave the room \n" + \
          "!q to quit \n"
    return msg


def handle_client(conn, addr):
    # Receives the nickname message from client
    name = conn.recv(1024).decode(FORMAT)
    this_user = User(conn, addr, name)
    # Adds the client to the list of clients
    clients.update({this_user.nick: this_user})
    # Adds the client to the list of users in the lobby
    ROOMS[0].users.append(this_user)
    # Prints to server console
    print(addr, " has joined as ", name)
    
    # Send options to client
    conn.send("You are in the lobby.".encode(FORMAT))
    conn.send(print_options().encode(FORMAT))
    
    # Loops until connected is False (client sends '!q')
    connected = True
    # XXX ADD FUNCTIONALITY TO THIS WHILE LOOP
    while connected:
        curr_room = ROOMS[this_user.room]
        # attempts to receive message from the client
        msg = conn.recv(1024).decode(FORMAT)

        # Does not enter if statement unless a message has been received
        if not msg == '':
            # msg_length = int(msg_length)
            if msg == '!q':
                connected = False
                disc_str = addr[0] + ":" + str(addr[1]) + " has disconnected"
                print(disc_str)
                curr_room.buffer.append(disc_str)
            else:
                print(addr, ":", msg)
                new_msg = this_user.nick + ": " + msg
                curr_room.buffer.append(new_msg)

        # Pops the buffer and sends the messages to all clients
        while curr_room.buffer:
            new_msg = curr_room.buffer.pop()
            for i in curr_room.users:
                i.conn.send(new_msg.encode(FORMAT))
        time.sleep(1)
    conn.close()


def start():
    # Initializing lobby room
    lobby = Room()
    ROOMS.append(lobby)
    server.listen()
    print("Server address: ", SERVER)
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active Connections: ", threading.active_count()-1, "\n")


print("Starting server...")
start()
