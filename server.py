import socket
import threading
import re  

connected_clients = {}  # links user's nicknames to their  sockets
channel_users = {}  # links channel names to the list of users in that channel

valid_commands = {"NICK", "JOIN", "PRIVMSG", "RECONNECT","WHO", "NEWSERVER", "CAP"}  # to make sure valid commands are run, we made a set 

def send_to_channel(message, exclude_client=None, channel=None):
    # Broadcast a message to all users in a channel, except the sender
    if channel:
        for user_nick in channel_users[channel]:
            client_socket = connected_clients[user_nick]
            if client_socket != exclude_client:
                client_socket.send(f"{message}\r\n".encode())  # Send with CRLF to comply with IRC protocol
    else:
        for client_socket in connected_clients.values():
            if client_socket != exclude_client:
                client_socket.send(f"{message}\r\n".encode())

def handle_client(client_socket, client_address):
    # Manage a connected client, handling various IRC commands
    print(f"Connection established from {client_address}")
    user_nick = None

    try:
        while True:
            incoming_data = client_socket.recv(1024).decode().strip()

            if not incoming_data:
                break

            # Parse the incoming command and check if it's valid
            command = incoming_data.split()[0]
            if command not in valid_commands:
                client_socket.send(f":IRCServer 421 * {command} :Unknown command\r\n".encode())
                continue

            # Handle NICK command
            if command == "NICK":
                user_nick = incoming_data.split()[1]

                if re.match(r'^[^a-zA-Z0-9]', user_nick):  # To handle if the nickname starts with any symbols
                    client_socket.send(f":IRCServer 432 - {user_nick} : Nicknames cannot start with symbols\r\n".encode())
                    continue

                # Check if the nickname is already taken
                elif user_nick in connected_clients:
                    client_socket.send(f":IRCServer 433 - {user_nick} :Nickname is already in use\r\n".encode())
                    
                else:
                    connected_clients[user_nick] = client_socket
                    client_socket.send(f":IRCServer 001 {user_nick} :Welcome to the IRC server!\r\n".encode()) 
                    print(f"User '{user_nick}' has joined the server.")

            # Handle JOIN commandS
            elif command == "JOIN":
                if not user_nick:
                    client_socket.send(":IRCServer 431 * :No nickname given\r\n".encode())  # Error if no nickname set
                    continue

                channel_name = incoming_data.split()[1]

                # Add the user to the channel
                if channel_name not in channel_users:
                    channel_users[channel_name] = []
                channel_users[channel_name].append(user_nick)

                send_to_channel(f":{user_nick} JOIN {channel_name}", channel=channel_name)
                print(f"User '{user_nick}' joined channel {channel_name}")

                # Send list of users in the channel
                users_in_channel = " ".join(channel_users[channel_name])
                client_socket.send(f":IRCServer 353 {user_nick} = {channel_name} :{users_in_channel}\r\n".encode())
                client_socket.send(f":IRCServer 366 {user_nick} {channel_name} :End of /NAMES list\r\n".encode())

            # Handle PRIVMSG command (sending messages to a channel or a user)
            elif command == "PRIVMSG":
                parts = incoming_data.split(':', 1)
                recipient = parts[0].split()[1]
                message_body = parts[1]
                print(f"{user_nick} -> {recipient}: {message_body}")

                if recipient.startswith("#"):  # Message to a channel
                    if recipient in channel_users:
                        send_to_channel(f":{user_nick} PRIVMSG {recipient} :{message_body}", exclude_client=client_socket, channel=recipient)
                    else:
                        client_socket.send(f":IRCServer 403 {user_nick} {recipient} :No such channel\r\n".encode())
                else:  # Private message to a user
                    if recipient in connected_clients:
                        target_socket = connected_clients[recipient]
                        target_socket.send(f":{user_nick} PRIVMSG {recipient} :{message_body}\r\n".encode())
                    else:
                        client_socket.send(f":IRCServer 401 {user_nick} {recipient} :No such nick/channel\r\n".encode())
        
    except Exception as e:
         print(f"Error: {e}")
    
    finally:
        # Remove the user on disconnect
        if user_nick and user_nick in connected_clients:
            del connected_clients[user_nick]
            for channel, users in channel_users.items():
                if user_nick in users:
                    users.remove(user_nick)
                    send_to_channel(f":{user_nick} has left {channel}\r\n", channel=channel)

        client_socket.close()

def run_server():
   # Initialize and run the IRC server 
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_socket.bind(("::", 6667))  # Listen on IPv6 address
    server_socket.listen(5)
    print("IRC Server is listening on port 6667...")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    run_server()
