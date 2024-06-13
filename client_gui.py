import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import threading
import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
CREATE_ROOM = "!CREATE"
JOIN_ROOM = "!JOIN"
LEAVE_ROOM = "!LEAVE"
LIST_ROOMS = "!LIST"
REGISTER = "!REGISTER"
LOGIN = "!LOGIN"
SERVER = "10.101.57.124"
ADDR = (SERVER, PORT)
HANDLE_CURRENTROOM_FALSE = "!CURRENTROOM"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

authenticated = False


def receive_messages():
    while True:
        try:
            message = client.recv(2048).decode(FORMAT)
            print(message)
            if message:
                if "successful" in message:
                    global authenticated
                    authenticated = True
                if "Registration successful." in message:
                    break
                if "Login successful." in message:
                    break
                if "The room owner has left the room. You have been removed from the room" in message:
                    send_message(HANDLE_CURRENTROOM_FALSE)

                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, message + '\n', 'received')
                chat_box.yview(tk.END)
                chat_box.config(state=tk.DISABLED)
        except Exception as e:
            print(e)
            client.close()
            break


def send_message(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    if (msg[:9] != REGISTER and msg[:6] != LOGIN and msg[:12] != HANDLE_CURRENTROOM_FALSE):
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {msg}\n", 'sent')
        chat_box.yview(tk.END)
        chat_box.config(state=tk.DISABLED)


def main_page():
    global window
    window = tk.Tk()
    window.title("Main Page")

    login_button = tk.Button(window, text="Login", command=on_login)
    login_button.pack()

    register_button = tk.Button(window, text="Register", command=on_register)
    register_button.pack()

    window.mainloop()


def chat_page():
    global window, message_entry
    window = tk.Tk()
    window.title("Chat Client")

    frame = tk.Frame(window)
    scrollbar = tk.Scrollbar(frame)
    global chat_box
    chat_box = scrolledtext.ScrolledText(
        frame, state=tk.DISABLED, wrap=tk.WORD)
    chat_box.tag_config('sent', justify='right')
    chat_box.tag_config('received', justify='left')
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame.pack(expand=True, fill=tk.BOTH)

    message_entry = tk.Entry(window)
    message_entry.pack(fill=tk.X, padx=10, pady=10)

    send_button = tk.Button(window, text="Send", command=on_send)
    send_button.pack()

    create_room_button = tk.Button(
        window, text="Create Room", command=on_create_room)
    create_room_button.pack(side=tk.LEFT)

    join_room_button = tk.Button(
        window, text="Join Room", command=on_join_room)
    join_room_button.pack(side=tk.LEFT)

    leave_room_button = tk.Button(
        window, text="Leave Room", command=on_leave_room)
    leave_room_button.pack(side=tk.LEFT)

    list_rooms_button = tk.Button(
        window, text="List Rooms", command=on_list_rooms)
    list_rooms_button.pack(side=tk.LEFT)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    window.mainloop()


def on_login():
    email = simpledialog.askstring("Login", "Enter email:")
    password = simpledialog.askstring("Login", "Enter password:", show='')
    if email and password:
        send_message(f"{LOGIN} {email} {password}")
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()
        receive_thread.join()
        if authenticated:
            window.withdraw()
            chat_page()


def on_register():
    email = simpledialog.askstring("Register", "Enter email:")
    password = simpledialog.askstring("Register", "Enter password:", show='')
    username = simpledialog.askstring("Register", "Enter username:")
    if email and password and username:
        send_message(f"{REGISTER} {email} {password} {username}")
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()
        receive_thread.join()
        if authenticated:
            window.withdraw()
            chat_page()


def on_send():
    global message_entry
    msg = message_entry.get()
    send_message(msg)
    message_entry.delete(0, tk.END)
    if msg == DISCONNECT_MESSAGE:
        window.quit()


def on_create_room():
    if authenticated:
        room_name = simpledialog.askstring("Create Room", "Enter room name:")
        if room_name:
            send_message(f"{CREATE_ROOM} {room_name}")
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


def on_join_room():
    if authenticated:
        room_name = simpledialog.askstring("Join Room", "Enter room name:")
        if room_name:
            send_message(f"{JOIN_ROOM} {room_name}")
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


def on_leave_room():
    if authenticated:
        send_message(LEAVE_ROOM)
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


def on_list_rooms():
    if authenticated:
        print("heree")
        send_message(LIST_ROOMS)
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


def on_closing():
    send_message(DISCONNECT_MESSAGE)
    print("logged out")
    window.destroy()


# Thread untuk halaman utama (login/register)
main_page_thread = threading.Thread(target=main_page)
main_page_thread.start()
