import socket
import threading
import time
import signal


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


SERVER = socket.gethostbyname(socket.gethostname())
PORT = 64444
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
rooms = []
names = []
threads = []

# Creating the socket and binding the local address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(ADDR)
except OSError:
    print('The server is already running, closing now')
    exit(1)

# Setting socket options for timeout
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.settimeout(0.2)


def graceful_exit(signal_received, frame):
    print("Shut down the server? (y/n)")
    if input() == 'y':
        for i in threads:
            i[0].close()
            i[1].join()
        exit(0)


signal.signal(signal.SIGINT, graceful_exit)


def print_options() -> str:
    msg = "\n===================\n" + \
          "!h for help \n" + \
          "!v to view_rooms the list of rooms \n" + \
          "!c to create a room \n" + \
          "!j to join a room \n" + \
          "!l to leave_room the room \n" + \
          "!s to send a message to specific rooms \n" + \
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
        user.conn.send("Invalid room number".encode(FORMAT))
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


# Receive messages from client, adds to message to separate room buffers, and distributes buffers to rooms
def handle_client(conn, addr):
    global rooms
    # Receives the nickname message from client
    connected = True
    this_user = None
    while connected:
        try:
            name = conn.recv(1024).decode(FORMAT)
            # Checks for unique name
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
                try:
                    msg = conn.recv(1024).decode(FORMAT)
                    args = msg.split(' ')

                    # Does not enter if statement unless a message has been received
                    if not msg == '':
                        # Checking for options
                        if args[0] == '!q':
                            conn.send(('quit').encode(FORMAT))
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
                                conn.send("Try again with proper room number \n".encode(FORMAT))
                                view_rooms(conn)
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
                        elif args[0] == '!s':
                            if len(rooms) < 1:
                                conn.send("Create a room first".encode(FORMAT))
                            elif len(this_user.rooms) < 1:
                                conn.send("Join a room first".encode(FORMAT))
                            else:
                                conn.send("Which rooms?".encode(FORMAT))
                                temp = conn.recv(1024).decode(FORMAT)
                                room_selection = temp.split(' ')
                                conn.send("Enter your message: ".encode(FORMAT))
                                s_message = conn.recv(1024).decode(FORMAT)
                                print(this_user.addr, ":", s_message)
                                new_msg = this_user.nick + ": " + s_message
                                for i in room_selection:
                                    if int(i) in this_user.rooms:
                                        rooms[int(i)].buffer.append(new_msg)
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
                except (ConnectionResetError, ConnectionAbortedError, ConnectionError):
                    this_user.conn.close()
                    break
                except ConnectionRefusedError:
                    print('The client connection is refused')
                    this_user.conn.close()
                    break
        except (ConnectionResetError, ConnectionAbortedError, ConnectionError, Exception):
            conn.close()
            if this_user:
                for i in this_user.rooms:
                    rooms[i].users.pop(this_user.nick)
                names.remove(this_user.nick)
            break


# Handles thread creation for client handling and listening
def start():
    # Initializing lobby room
    global threads
    lobby = Room()
    rooms.append(lobby)
    server.listen()
    print("Server address: ", SERVER)
    while True:
        try:
            (conn, addr) = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            threads.append((conn, thread))
            print("Active Connections: ", threading.active_count()-1, "\n")
        except TimeoutError:
            pass
        except KeyboardInterrupt:
            signal.raise_signal(signal.SIGINT)


print("Starting server...")
print("Use ctrl+c to exit")
start()
