# server.py
import socket
import threading
import hashlib

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CREATE_ROOM = "!CREATE"
JOIN_ROOM = "!JOIN"
LEAVE_ROOM = "!LEAVE"
LIST_ROOMS = "!LIST"
REGISTER = "!REGISTER"
LOGIN = "!LOGIN"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

rooms = {}
clients = {}
# Dictionary to store user data (email -> (username, hashed_password))
users = {}


def broadcast(message, room, exception=None):
    # client adalah conn
    for client in rooms[room]:
        if client != exception:
            client.send(message.encode(FORMAT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    current_room = None
    authenticated = False
    username = None

    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    if current_room:
                        rooms[current_room].remove(conn)
                        broadcast(f"[{username}] left the room.", current_room)
                        if not rooms[current_room]:
                            del rooms[current_room]
                    break

                if not authenticated:
                    if msg.startswith(REGISTER):
                        _, email, password, username = msg.split(maxsplit=3)
                        if email in users:
                            conn.send(
                                "Email already registered.".encode(FORMAT))
                        else:
                            hashed_password = hashlib.sha256(
                                password.encode()).hexdigest()
                            users[email] = (username, hashed_password)
                            authenticated = True
                            conn.send(
                                "Registration successful.".encode(FORMAT))

                    elif msg.startswith(LOGIN):
                        _, email, password = msg.split(maxsplit=2)
                        if email in users and users[email][1] == hashlib.sha256(password.encode()).hexdigest():
                            authenticated = True
                            username = users[email][0]
                            conn.send(
                                f"Login successful. Welcome {username}!".encode(FORMAT))
                        else:
                            conn.send(
                                "Invalid email or password.".encode(FORMAT))
                    continue

                # Process other commands only if authenticated
                if msg.startswith(CREATE_ROOM):
                    _, room_name = msg.split(maxsplit=1)
                    if room_name not in rooms:
                        rooms[room_name] = []
                        conn.send(f"Room {room_name} created.".encode(FORMAT))
                    else:
                        conn.send(
                            f"Room {room_name} already exists.".encode(FORMAT))

                elif msg.startswith(JOIN_ROOM):
                    _, room_name = msg.split(maxsplit=1)
                    if room_name in rooms:
                        if current_room:
                            rooms[current_room].remove(conn)
                        rooms[room_name].append(conn)
                        current_room = room_name
                        conn.send(f"Joined room {room_name}".encode(FORMAT))
                        broadcast(f"[{username}] joined the room.",
                                  current_room, conn)
                    else:
                        conn.send(
                            f"Room {room_name} does not exist.".encode(FORMAT))

                elif msg.startswith(LEAVE_ROOM):
                    if current_room:
                        rooms[current_room].remove(conn)
                        broadcast(f"[{username}] left the room.", current_room)
                        if not rooms[current_room]:
                            del rooms[current_room]
                        current_room = None
                        conn.send("Left the room.".encode(FORMAT))
                    else:
                        conn.send("You are not in any room.".encode(FORMAT))

                elif msg == LIST_ROOMS:
                    room_list = "Available rooms:\n" + "\n".join(rooms.keys())
                    print(conn)
                    conn.send(room_list.encode(FORMAT))

                else:
                    if current_room:
                        broadcast(f"[{username}] {msg}", current_room, conn)
                    else:
                        conn.send("You are not in any room.".encode(FORMAT))

        except Exception as e:
            print(f"[ERROR] {e}")
            connected = False

    if current_room and conn in rooms[current_room]:
        rooms[current_room].remove(conn)
        broadcast(f"[{username}] left the room.", current_room)
        if not rooms[current_room]:
            del rooms[current_room]

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()
