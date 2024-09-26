import socket


def send_message_as_bot(sock, message): # this function is used to send messages to the channel as a bot
    sock.send((message + "\r\n").encode())

def bot_join_channel(sock, channel):   # bot can join a channel 
    send_message_as_bot(sock, f"JOIN {channel}")

def respond_to_messages(sock, channel, user, command): # responds to messages with ! mark
    if command == "!hello":
        print('Hello Recieved')
        send_message_as_bot(sock, f"PRIVMSG {channel} :Hello, {user}!")

# this function ensures that the input text exists,if blank, it uses a default value
def get_input(prompt_text, default_value=None):
    user_input = input(f"{prompt_text} (default: {default_value}): ").strip()
    return user_input if user_input else default_value

def main():
    # default input values
    default_server = "::1"
    default_port = 6667
    default_nickname = "SuperBot"
    default_channel = "#test"

    # inputs with default placeholders & validation
    print("---------------------------------------------------------------------")
    print('Default values are shown in the bracket, just press enter to continue')
    server = get_input("Enter the IRC server address (IPv6)", default_server)
    port = get_input("Enter the port your server is running on", default_port)
    nickname = get_input("Enter your bot's nickname", default_nickname)
    channel = get_input("Enter the channel to join", default_channel)

    # socket connection 
    socket_connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    socket_connection.connect((server, int(port)))

    send_message_as_bot(socket_connection, f"NICK {nickname}")
    send_message_as_bot(socket_connection, f"USER {nickname} 0 * :SuperBot")

    

    # join channel once connected
    bot_join_channel(socket_connection, channel)

    while True:
        data = socket_connection.recv(1024).decode() # receiving the raw log data here
        print("Raw data received:", data)

        # keeping the server connection alive
        if data.startswith("PING"):
            send_message_as_bot(socket_connection, f"PONG {data.split()[1]}")

        # detecting the PRIVMSG keyword and trying to parse
        elif "PRIVMSG" in data:
            parts = data.split(" :", 1)  
            if len(parts) > 1:
                message = parts[1].strip()
                user_info = data.split("!")[0]
                user = user_info.split(":")[1].strip()
                print(f"Message from {user} -> {message}")

                # ! mark detection 
                if message.startswith("!"):
                    respond_to_messages(socket_connection, channel, user, message)

if __name__ == "__main__":
    main()
