import socket
import threading
import time


class User:
    def __init__(self, new_conn, new_addr, new_nick):
        self.conn = new_conn
        self.addr = new_addr
        self.nick = new_nick
        self.rooms = [0]
        
        
class Room:
    def __init__(self):
        self.buffer = []
        self.users = {}


# SERVER = '127.0.0.1'
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 64444
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
rooms = []
names = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server_on = True


def print_options() -> str:
    msg = "\n===================\n" + \
          "!h for help \n" + \
          "!v to view_rooms the list of rooms \n" + \
          "!c to create a room \n" + \
          "!j to join a room \n" + \
          "!l to leave_room the room \n" + \
          "!q to quit \n"
    return msg


def create_room(user):
    global rooms
    new_room = Room()
    new_room.users.update({user.nick: user})
    rooms.append(new_room)
    user.rooms.append(len(rooms) - 1)
    user.conn.send(("You have joined room " + str(len(rooms) - 1) + '\n').encode(FORMAT))


def join_room(room_number, user) -> bool:
    global rooms
    room_number = int(room_number)
    if room_number < len(rooms):
        if room_number not in user.rooms:
            # update room number for user
            user.rooms.append(room_number)
            # add user to the requested room
            rooms[room_number].users.update({user.nick: user})
            return True
        else:
            user.conn.send(("Already in room " + str(room_number) + "\n").encode(FORMAT))
            return False
    else:
        return False


def leave_room(user, room_number) -> bool:
    global rooms
    room_number = int(room_number)
    if room_number < len(rooms):
        user_list = rooms[room_number].users
        if user.nick in user_list.keys():
            user_list.pop(user.nick)
            user.rooms.remove(room_number)
            return True
        else:
            return False
    return False


def view_rooms(conn):
    conn.send("===================\nRooms available:\n".encode(FORMAT))

    for i in rooms:
        index = str(rooms.index(i))
        conn.send(("  +  " + index + "\n").encode(FORMAT))
        for j in i.users.keys():
            conn.send(("    -" + j).encode(FORMAT))
            conn.send('\n'.encode(FORMAT))
        conn.send('\n\n'.encode(FORMAT))


def handle_client(conn, addr):
    # Receives the nickname message from client
    connected = True
    while server_on and connected:
        name = conn.recv(1024).decode(FORMAT)
        while name in names:
            conn.send('Please use another username'.encode(FORMAT))
            name = conn.recv(1024).decode(FORMAT)
        names.append(name)
        this_user = User(conn, addr, name)
        # Adds the client to the list of users in the lobby
        rooms[0].users.update({this_user.nick: this_user})
        # Prints to server console
        print(addr, " has joined as ", name)
        
        # Send options to client
        conn.send("You are in the lobby.".encode(FORMAT))
        conn.send(print_options().encode(FORMAT))
        
        # Loops until connected is False (client sends '!q')
        while connected:
            # attempts to receive message from the client
            msg = conn.recv(1024).decode(FORMAT)
            args = msg.split(' ')

            # Does not enter if statement unless a message has been received
            if not msg == '':
                if args[0] == '!q':
                    conn.close()
                    connected = False
                    disc_str = addr[0] + ":" + str(addr[1]) + " has disconnected"
                    print(disc_str)
                    for i in this_user.rooms:
                        rooms[i].buffer.append(disc_str)
                        rooms[i].users.pop(this_user.nick)
                    names.remove(this_user.nick)
                elif args[0] == '!h':
                    conn.send(print_options().encode(FORMAT))
                elif args[0] == '!v':
                    view_rooms(conn)
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
                    conn.send("Enter a room number: ".encode(FORMAT))
                    room_number = conn.recv(1024).decode(FORMAT)
                    if leave_room(this_user, room_number):
                        conn.send(("you have left room " + str(room_number)).encode(FORMAT))
                    else:
                        conn.send("Can't leave room".encode(FORMAT))
                    view_rooms(conn)
                else:
                    print(addr, ":", msg)
                    new_msg = this_user.nick + ": " + msg
                    for i in this_user.rooms:
                        rooms[i].buffer.append(new_msg)

            # Pops the buffer and sends the messages to all clients
            sent_list = []
            for i in this_user.rooms:
                while rooms[i].buffer:
                    new_msg = rooms[i].buffer.pop()
                    user_list = rooms[i].users
                    for j in rooms[i].users.keys():
                        if j not in sent_list:
                            sent_list.append(j)
                            user_list.get(j).conn.send(new_msg.encode(FORMAT))
            time.sleep(1)


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
