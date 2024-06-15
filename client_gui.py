import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import threading
import socket
import time

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
SERVER = "192.168.1.5"
ADDR = (SERVER, PORT)
HANDLE_CURRENTROOM_FALSE = "!CURRENTROOM"
MSGUSER = "!MSGUSER"
ABOUT = "!ABOUT"
KICKUSER = "!KICKUSER"
OWNER = "!OWNER"
WELCOMEMSG = "!WELCOMEMSG"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

authenticated = False


def receive_messages():
    while True:
        try:
            message = client.recv(2048).decode(FORMAT)
            print(message)
            if message:
                if "!MSGUSER" in message:
                    message = message[8:]
                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(tk.END, message + '\n', 'received')
                    chat_box.yview(tk.END)
                    chat_box.config(state=tk.DISABLED)
                    continue
                if "!successful" in message:
                    global authenticated
                    authenticated = True
                if "!Registration !successful." in message:
                    break
                if "!Login !successful." in message:
                    break
                if "!Email already registered." in message:
                    error_page("Email already registered")
                    break
                if "!There is an error" in message:
                    error_page("There is an error")
                    break
                if "!Email not registered." in message:
                    error_page("Email not registered")
                    break
                if "!Invalid email or password." in message:
                    error_page("Invalid email or password")
                    break
                if "Joined room" in message:
                    on_clear_chat()

                if "!OWNERJoined room" in message:
                    addKickButton()

                    message = message[6:]

                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(tk.END, message + '\n', 'system')
                    chat_box.yview(tk.END)
                    chat_box.config(state=tk.DISABLED)

                    continue

                if "!KICKBUTTON" in message:
                    removeKickButton()
                    continue

                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, message + '\n', 'system')
                chat_box.yview(tk.END)
                chat_box.config(state=tk.DISABLED)

                if "The room owner has left the room. You have been removed from the room" in message:
                    send_message(HANDLE_CURRENTROOM_FALSE)
                    time.sleep(5)
                    on_clear_chat()
                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(
                        tk.END, f"Welcome back to main menu!\n", 'system')
                    chat_box.yview(tk.END)
                    chat_box.config(state=tk.DISABLED)
                elif "Left the room." in message:
                    on_clear_chat()
                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(
                        tk.END, f"Welcome back to main menu!\n", "system")
                    chat_box.yview(tk.END)
                    chat_box.config(state=tk.DISABLED)
                elif "You have been kicked from this room, you will exit the chat in 5 seconds, Goodbye!" in message:
                    send_message(HANDLE_CURRENTROOM_FALSE)
                    time.sleep(5)
                    on_clear_chat()
                    chat_box.config(state=tk.NORMAL)
                    chat_box.insert(
                        tk.END, f"Welcome back to main menu!\n", 'system')
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

    if (msg[:9] != REGISTER and msg[:6] != LOGIN and msg[:12] != HANDLE_CURRENTROOM_FALSE and msg[:11] != WELCOMEMSG):
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {msg}\n", 'sent')
        chat_box.yview(tk.END)
        chat_box.config(state=tk.DISABLED)


def error_page(msg):

    error_window = tk.Tk()
    error_window.title("Error Page")

    window_width = 300
    window_height = 100

    screen_width = error_window.winfo_screenwidth()
    screen_height = error_window.winfo_screenheight()

    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    error_window.geometry(
        f'{window_width}x{window_height}+{position_x}+{position_y}')

    error_label = tk.Label(error_window, text=msg, fg="red")
    error_label.pack(pady=10)

    close_button = tk.Button(error_window, text="Close",
                             command=error_window.destroy)
    close_button.pack(pady=10)

    error_window.mainloop()


def main_page():
    global window
    window = tk.Tk()
    window.title("Main Page")

    window_width = 300
    window_height = 100

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    window.geometry(
        f'{window_width}x{window_height}+{position_x}+{position_y}')

    login_button = tk.Button(window, text="Login",
                             command=lambda: on_login(window), padx=10, pady=5)
    login_button.pack(pady=5)
    register_button = tk.Button(
        window, text="Register", command=lambda: on_register(window), padx=10, pady=5)
    register_button.pack(pady=5)

    window.mainloop()


def chat_page():
    global window, message_entry
    window = tk.Tk()
    window.title("Chat Client")
    window.configure(background="gray89")

    frame = tk.Frame(window)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.configure(background="darkgray")
    global chat_box
    chat_box = scrolledtext.ScrolledText(
        frame, state=tk.DISABLED, wrap=tk.WORD)
    chat_box.configure(background="black")
    chat_box.tag_config('sent', justify='right', foreground="white")
    chat_box.tag_config('received', justify='left', foreground="white")
    chat_box.tag_config("system", justify="center", foreground="lightgreen")
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

    clear_chat_button = tk.Button(
        window, text="Clear Chat", command=on_clear_chat)
    clear_chat_button.pack(side=tk.RIGHT)

    about_button = tk.Button(
        window, text="About", command=on_about_button)
    about_button.pack(side=tk.RIGHT)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    send_message(f"{WELCOMEMSG}")
    window.mainloop()


def addKickButton():
    global window, kick_button
    kick_button = tk.Button(window, text="Kick", command=on_kick)
    kick_button.pack(side=tk.RIGHT)


def removeKickButton():
    global kick_button
    if (kick_button):
        kick_button.destroy()
        kick_button = None


def on_kick():
    email = simpledialog.askstring("Kick user", "Enter user email:")
    if (email):
        send_message(f"{KICKUSER} {email}")

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()
    window.mainloop()


def on_login(window):
    window.withdraw()
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


def on_register(window):
    window.withdraw()
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
    if (len(msg) > 0):
        send_message(msg)
        message_entry.delete(0, tk.END)
        if msg == DISCONNECT_MESSAGE:
            window.quit()


def on_create_room():
    if authenticated:
        room_name = simpledialog.askstring("Create Room", "Enter room name:")
        description_room = simpledialog.askstring(
            "Description Room", "Enter description room:")
        if room_name and description_room:
            send_message(f"{CREATE_ROOM} {room_name} {description_room}")
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
        send_message(LIST_ROOMS)
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


def on_closing():
    send_message(DISCONNECT_MESSAGE)
    print("logged out")
    window.destroy()


def on_clear_chat():
    chat_box.config(state=tk.NORMAL)
    chat_box.delete(1.0, tk.END)
    chat_box.config(state=tk.DISABLED)


def on_about_button():
    if authenticated:
        send_message(ABOUT)
    else:
        messagebox.showwarning("Authentication required",
                               "Please login first.")


# Thread untuk halaman utama (login/register)
main_page_thread = threading.Thread(target=main_page)
main_page_thread.start()
