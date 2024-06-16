# server.py
import socket
import threading
import hashlib

from connectDB import connectionDB

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
HANDLE_CURRENTROOM_FALSE = "!CURRENTROOM"
MSGUSER = "!MSGUSER"
ABOUT = "!ABOUT"
KICKUSER = "!KICKUSER"
OWNER = "!OWNER"
KICKBUTTON = "!KICKBUTTON"
WELCOMEMSG = "!WELCOMEMSG"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

rooms = {}
room_owner = {}
descriptionRooms = {}
dictParticipantsInRoom = {}


def broadcast(message, room, exception=None):
    for client in rooms[room]:
        if client != exception:
            client.send(message.encode(FORMAT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    current_room = None
    authenticated = False
    username = None
    email = None

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

                        checkEmail = checkIsEmailExist(email)
                        if checkEmail == True:
                            conn.send(
                                "!Email already registered.".encode(FORMAT))
                        else:
                            hashed_password = hashlib.sha256(
                                password.encode()).hexdigest()
                            statusMasukanUser = registerUser(
                                email, username, hashed_password)
                            if (statusMasukanUser == True):
                                authenticated = True
                                conn.send(
                                    "!Registration !successful.".encode(FORMAT))
                            else:
                                conn.send(
                                    "!There is an error".encode(FORMAT))

                    elif msg.startswith(LOGIN):
                        _, emailLogin, password = msg.split(maxsplit=2)
                        hashed_password = hashlib.sha256(
                            password.encode()).hexdigest()
                        checkEmail = checkIsEmailExist(emailLogin)
                        if checkEmail == False:
                            conn.send(
                                "!Email not registered.".encode(FORMAT))
                        else:
                            dictUserData = getUserData(emailLogin)
                            hashed_password_from_db = dictUserData["Hashed_DB_Password"]
                            if hashed_password == hashed_password_from_db:
                                authenticated = True
                                username = dictUserData["Username"]
                                email = emailLogin
                                conn.send(
                                    f"!Login !successful. Welcome {username}!".encode(FORMAT))
                            else:
                                conn.send(
                                    "!Invalid email or password.".encode(FORMAT))
                    continue

                if msg.startswith(CREATE_ROOM):
                    _, room_name, descRoom = msg.split(maxsplit=2)
                    if room_name not in rooms:
                        rooms[room_name] = []
                        room_owner[room_name] = conn
                        descriptionRooms[room_name] = descRoom
                        dictParticipantsInRoom[room_name] = {}
                        dictParticipantsInRoom[room_name][email] = (
                            conn, username)
                        conn.send(f"Room {room_name} created.".encode(FORMAT))
                    else:
                        conn.send(
                            f"Room {room_name} already exists.".encode(FORMAT))

                elif msg.startswith(JOIN_ROOM):
                    _, room_name = msg.split(maxsplit=1)
                    if room_name in rooms:
                        if current_room:
                            conn.send(
                                "You are currently in a room, you must leave this room first!".encode(FORMAT))
                            continue
                        rooms[room_name].append(conn)
                        current_room = room_name
                        dictParticipantsInRoom[room_name][email] = (
                            conn, username)
                        if (room_owner[room_name] != conn):
                            conn.send(
                                f"Joined room {room_name}".encode(FORMAT))
                        else:
                            conn.send(
                                f"{OWNER}Joined room {room_name}".encode(FORMAT))
                        broadcast(f"[{username}] joined the room.",
                                  current_room, conn)
                    else:
                        conn.send(
                            f"Room {room_name} does not exist.".encode(FORMAT))

                elif msg.startswith(LEAVE_ROOM):
                    if current_room:
                        dictParticipantsInRoom[current_room].pop(email)
                        rooms[current_room].remove(conn)
                        broadcast(f"[{username}] left the room.", current_room)
                        if room_owner[current_room] == conn:
                            conn.send(KICKBUTTON.encode(FORMAT))
                            for member in rooms[current_room]:
                                member.send(
                                    "The room owner has left the room. You have been removed from the room, you will exit the chat in 5 seconds, Goodbye!".encode(FORMAT))
                            del rooms[current_room]
                            del room_owner[current_room]
                            del descriptionRooms[current_room]
                            del dictParticipantsInRoom[current_room]
                        current_room = None
                        conn.send("Left the room.".encode(FORMAT))
                    else:
                        conn.send("You are not in any room.".encode(FORMAT))

                elif msg.startswith(KICKUSER):
                    _, emailKickedUser = msg.split(maxsplit=1)
                    dataUser = dictParticipantsInRoom[current_room].get(
                        emailKickedUser)
                    if (dataUser == None):
                        conn.send("User email doesn't exist")
                    else:
                        userKickedConn = dataUser[0]
                        usernameKickedUser = dataUser[1]

                        broadcast(
                            f"[{usernameKickedUser}] has been kicked from this room", current_room, userKickedConn)

                        userKickedConn.send(
                            "You have been kicked from this room, you will exit the chat in 5 seconds, Goodbye!".encode(FORMAT))

                        dictParticipantsInRoom[current_room].pop(
                            emailKickedUser)
                        rooms[current_room].remove(userKickedConn)

                elif msg == LIST_ROOMS:
                    room_list = "Available rooms:\n" + "\n".join(rooms.keys())
                    print(conn)
                    conn.send(room_list.encode(FORMAT))

                elif msg == HANDLE_CURRENTROOM_FALSE:
                    current_room = False

                elif msg.startswith(ABOUT):
                    if (current_room):
                        dictUserDiRoom = dictParticipantsInRoom[current_room]
                        messageResult = "Description about room:\n"
                        messageResult = messageResult + \
                            descriptionRooms[current_room] + "\n\n"

                        messageResult = messageResult + "Participants in room: \n"

                        connOwner = room_owner[room_name]
                        for currTuple in dictUserDiRoom.items():
                            emailUser = currTuple[0]

                            connUser = currTuple[1][0]
                            usernameUser = currTuple[1][1]

                            if (connUser == connOwner):
                                messageResult = messageResult + usernameUser + \
                                    "     " + " (*OWNER*)" + "\n"
                            else:
                                messageResult = messageResult + usernameUser + "     " + emailUser + "\n"

                        conn.send(messageResult.encode(FORMAT))

                    else:
                        conn.send("You are in lobby room".encode(FORMAT))

                elif msg == WELCOMEMSG:
                    conn.send(f"Welcome to lobby {username}!".encode(FORMAT))
                else:
                    if current_room:
                        broadcast(
                            f"!MSGUSER[{username}] {msg}", current_room, conn)
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


def checkIsEmailExist(Email):
    SQL_QUERY = '''
    SELECT Email FROM Client WHERE Email = ?
    '''

    result = connectionDB.execute(SQL_QUERY, (Email)).fetchone()

    if (result != None):
        # kalau email nya udah kepake
        return True
    else:
        # kalau email nya belum kepake orang lain
        return False


def getUserData(Email):
    SQL_QUERY = '''
    SELECT Username, Password FROM CLIENT WHERE Email = ?
    '''
    result = connectionDB.execute(SQL_QUERY, (Email)).fetchone()

    dictDataUser = {
        "Username": result[0],
        "Hashed_DB_Password": result[1]
    }

    return dictDataUser


def registerUser(Email, Username, Password):
    SQL_QUERY = '''
    INSERT INTO CLIENT(Email, Username, Password)
    VALUES(?, ?, ?)
    '''

    try:
        connectionDB.execute(SQL_QUERY, (Email, Username, Password))
        connectionDB.commit()
        return True
    except:
        return False


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
