import socket
import random
import threading
import tkinter as tk
from tkinter import scrolledtext, Toplevel

# Fun fact database
fun_facts = [
    "Bananas are berries, but strawberries aren't.",
    "A group of flamingos is called a 'flamboyance'.",
    "Honey never spoils. Archaeologists have found pots of honey over 3,000 years old!"
]

class IRCBot:
    def __init__(self, server, port, nickname, channel, log_widget):
        self.server = server
        self.port = port
        self.nickname = nickname
        self.channel = channel
        self.log_widget = log_widget
        self.sock = None

    def send_message(self, message):
        """Send a message to the IRC server."""
        if self.sock:
            self.sock.send((message + "\r\n").encode())

    def join_channel(self):
        """Join a channel."""
        self.send_message(f"JOIN {self.channel}")

    def respond_to_command(self, user, command):
        """Respond to channel commands."""
        if command == "!hello":
            self.log(f"Hello command received from {user}")
            self.send_message(f"PRIVMSG {self.channel} :Hello, {user}!")
        elif command.startswith("!slap"):
            words = command.split()
            target = random.choice(["User1", "User2", "User3"])  # Placeholder for random users
            if len(words) > 1:
                target = words[1]
            self.send_message(f"PRIVMSG {self.channel} :{user} slaps {target} with a trout!")

    def respond_to_private_message(self, user):
        """Respond to private messages with random fun facts."""
        fun_fact = random.choice(fun_facts)
        self.send_message(f"PRIVMSG {user} :{fun_fact}")
        self.log(f"Sent fun fact to {user}: {fun_fact}")

    def log(self, message):
        """Log messages to the log_widget."""
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)  # Auto-scroll to the end of the log

    def start(self):
        """Start the IRC bot."""
        try:
            # Create a socket and connect to the IRC server
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.sock.connect((self.server, self.port))

            # Send user and nickname info
            self.send_message(f"NICK {self.nickname}")
            self.send_message(f"USER {self.nickname} 0 * :SuperBot")

            # Join the channel
            self.join_channel()

            self.log(f"Connected to {self.channel} as {self.nickname}")

            while True:
                # Receive data from the server
                data = self.sock.recv(1024).decode()

                # Handle PING (keep-alive)
                if data.startswith("PING"):
                    self.send_message(f"PONG {data.split()[1]}")

                # Parse message
                elif "PRIVMSG" in data:
                    parts = data.split(" :", 1)
                    
                    if len(parts) > 1:
                        message = parts[1].strip()

                        user_info = data.split("!")[0]
                        user = user_info.split(":")[1].strip()

                        self.log(f"Message from {user}: {message}")

                        if message.startswith("!"):
                            self.respond_to_command(user, message)
        except Exception as e:
            self.log(f"Error: {e}")

class BotWindow:
    """Represents a single bot window where the user can configure and launch a bot."""
    
    def __init__(self, root, server="", nickname="", channel=""):
        """Create a new bot configuration window."""
        self.window = Toplevel(root)
        self.window.title("Bot Configuration")

        # Store the input fields for this bot
        self.server_entry = tk.Entry(self.window, width=40)
        self.server_entry.insert(0, server)

        self.nickname_entry = tk.Entry(self.window, width=40)
        self.nickname_entry.insert(0, nickname)

        self.channel_entry = tk.Entry(self.window, width=40)
        self.channel_entry.insert(0, channel)

        # Log widget for this bot
        self.log_widget = scrolledtext.ScrolledText(self.window, width=60, height=20)

        # Layout configuration
        tk.Label(self.window, text="IRC Server (IPv6):").grid(row=0, column=0, padx=5, pady=5)
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.window, text="Bot Nickname:").grid(row=1, column=0, padx=5, pady=5)
        self.nickname_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.window, text="Channel:").grid(row=2, column=0, padx=5, pady=5)
        self.channel_entry.grid(row=2, column=1, padx=5, pady=5)

        log_label = tk.Label(self.window, text="Bot Log:")
        log_label.grid(row=3, column=0, padx=5, pady=5)
        self.log_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Button to connect the bot
        connect_button = tk.Button(self.window, text="Connect", command=self.on_connect)
        connect_button.grid(row=5, column=0, columnspan=2, pady=10)

    def on_connect(self):
        """Handle the bot connection for this window."""
        server = self.server_entry.get()
        nickname = self.nickname_entry.get()
        channel = self.channel_entry.get()

        if server and nickname and channel:
            self.log_widget.insert(tk.END, f"Connecting bot for {channel} as {nickname}...\n")
            port = 6667  # IRC port
            new_bot = IRCBot(server, port, nickname, channel, self.log_widget)

            # Start the bot in a new thread
            bot_thread = threading.Thread(target=new_bot.start)
            bot_thread.start()
        else:
            self.log_widget.insert(tk.END, "Please fill all the fields.\n")
        self.log_widget.see(tk.END)

class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRC Bot Manager")

        # List to keep track of all bot windows
        self.bot_windows = []

        self.setup_widgets()

    def setup_widgets(self):
        """Setup the main app GUI widgets."""
        tk.Label(self.root, text="Manage IRC Bots").grid(row=0, column=0, padx=10, pady=10)

        # Button to create a new bot window
        new_bot_button = tk.Button(self.root, text="Create New Bot", command=self.create_new_bot_window)
        new_bot_button.grid(row=1, column=0, padx=10, pady=10)

    def create_new_bot_window(self):
        """Create a new bot window."""
        new_bot_window = BotWindow(self.root)
        self.bot_windows.append(new_bot_window)  # Keep track of the new window


if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
