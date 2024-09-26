import socket
import random


def send_message_as_bot(sock, message): # this function is used to send messages to the channel as a bot
    sock.send((message + "\r\n").encode())

def bot_join_channel(sock, channel):   # bot can join a channel 
    send_message_as_bot(sock, f"JOIN {channel}")

def respond_to_messages(sock, channel, user, command): # responds to messages with ! mark
    if command == "!hello":
        print('Hello Recieved')
        send_message_as_bot(sock, f"PRIVMSG {channel} :Hello, {user}!")

def check_if_its_minircd(port):
    if port == 6667:
        print("You are now connected to minircd's server!")
    else: 
        print("You are connected to a personal server now!")


# this funciton makes sures that the input text exists, and is not blank, if blank, it promps again
def get_input(prompt_text):
    user_input = ""
    while not user_input:
        user_input = input(prompt_text).strip() 
        if not user_input:
            print("This field cannot be empty. Please enter a value.")
    return user_input


def main():


   # inputs & validations
    server = get_input("Enter the IRC server address (IPv6): ")
    port = get_input('Enter the port your server is running on:')
    nickname = get_input("Enter your bot's nickname: ")
    channel = get_input("Enter the channel to join: ")  
    
    #socket connection
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.connect((server, int(port)))


    send_message_as_bot(sock, f"NICK {nickname}")
    send_message_as_bot(sock, f"USER {nickname} 0 * :SuperBot")

    check_if_its_minircd(int(port))

    # join channel once connected
    bot_join_channel(sock, channel)

    while True:
       
        data = sock.recv(1024).decode() # receieving the raw log data here
        print("Raw data received:", data)

        # keeping the server connection alive
        if data.startswith("PING"):
            send_message_as_bot(sock, f"PONG {data.split()[1]}")

        # detecting the PRIVMSg keyword and trying to parse
        elif "PRIVMSG" in data:
            parts = data.split(" :", 1)  
            
            if len(parts) > 1:
                message = parts[1].strip()
                user_info = data.split("!")[0]
                user = user_info.split(":")[1].strip()


                print(f"Message from {user}: {message}")

                # ! mark detection 
                if message.startswith("!"):
                    respond_to_messages(sock, channel, user, message)

if __name__ == "__main__":
    main()
