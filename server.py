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
        
SERVER= '127.0.0.1'
PORT= 64444
#SERVER = socket.gethostbyname(socket.gethostname())
#PORT = 5000
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
rooms = []
clients = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


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


def create_room(user):
    new_room = Room()
    new_room.users.append(user)
    rooms.append(new_room)
    rooms[user.room].users.remove(user)
    user.room = len(rooms) - 1
    user.conn.send(("You are now in room " + str(user.room)).encode(FORMAT))


def join_room(room_number, user):
    if rooms[room_number]:
        # remove user from current room
        #check if user is in current room because we can leave a room before joining another room (!l)
        if user in rooms[user.room].users:
            rooms[user.room].users.remove(user)
        # update room number for user
        user.room = room_number
        # add user to the requested room
        rooms[room_number].users.append(user)
        return True
    else:
        return False

def view(conn,addr):
    conn.send("Rooms available:   \n".encode(FORMAT))
    #userList = []
  
    for i in rooms:
        index=str(rooms.index(i))
        conn.send(index.encode(FORMAT))
        conn.send('\n'.encode(FORMAT))
        for j in i.users:
            name=j.nick 
            conn.send(name.encode(FORMAT))
            conn.send(' '.encode(FORMAT))   
        
                
def leave(conn,addr,user):
    room_number = user.room
    this_room = rooms[room_number]
    user_list = this_room.users
    if user_list:
        if user in user_list:
            user_list.remove(user) 

        
    
    
            
        
    
                 
def handle_client(conn, addr):
    # Receives the nickname message from client
    name = conn.recv(1024).decode(FORMAT)
    this_user = User(conn, addr, name)
    # Adds the client to the list of clients
    clients.update({this_user.nick: this_user})
    # Adds the client to the list of users in the lobby
    rooms[0].users.append(this_user)
    # Prints to server console
    print(addr, " has joined as ", name)
    
    # Send options to client
    conn.send("You are in the lobby.".encode(FORMAT))
    conn.send(print_options().encode(FORMAT))
    
    # Loops until connected is False (client sends '!q')
    connected = True
    # XXX ADD FUNCTIONALITY TO THIS WHILE LOOP
    while connected:
        curr_room = rooms[this_user.room]
        # attempts to receive message from the client
        msg = conn.recv(1024).decode(FORMAT)
        args = msg.split(' ')

        # Does not enter if statement unless a message has been received
        if not msg == '':
            if args[0] == '!q':
                connected = False
                disc_str = addr[0] + ":" + str(addr[1]) + " has disconnected"
                print(disc_str)
                curr_room.buffer.append(disc_str)
            elif args[0] == '!h':
                conn.send(print_options().encode(FORMAT))
            elif args[0] == '!v':
                view(conn,addr)
            elif args[0] == '!c':
                create_room(this_user)
            elif args[0] == '!j':
                conn.send("Enter a room number".encode(FORMAT))
                room_number = int(conn.recv(1024).decode(FORMAT))
                if not join_room(room_number, this_user):
                    conn.send("Invalid room number".encode(FORMAT))
                else:
                    conn.send(("You have joined room " + str(room_number)).encode(FORMAT))
            elif args[0] == '!l':
                leave(conn,addr,this_user)
                view(conn,addr)
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
    rooms.append(lobby)
    server.listen()
    print("Server address: ", SERVER)
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active Connections: ", threading.active_count()-1, "\n")


print("Starting server...")
start()
