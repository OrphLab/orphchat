import threading
import socket
from client import Client
import pickle
import datetime

# Set up socket
HOST = '127.0.0.1' 
PORT = 65432 

# create socket object with IPv4 and TCP protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# bind socket to host and port
server.bind((HOST, PORT)) 

# listen for connections
server.listen() 

now = datetime.datetime.now() 

# list to store clients
clients = []

# function to decode message from client
def message_decoder(message):
    try:
        received_message = pickle.loads(message)
        print(f"Received message: {received_message}")
        sender_nickname = received_message['nickname']
        message_content = received_message['message']
        decoded_message = (sender_nickname, message_content)
        return decoded_message
    except (UnicodeDecodeError, KeyError):
        print("Error decoding message")
    return 

# function to handle client connection and messages from client 
def receive_messages(client):
    while True:
        try:
            # receive message from client 
            received_bytes = client.socket.recv(4096)
            print(f'{len(received_bytes)} bytes received) from {client.nickname}')
            message = message_decoder(received_bytes)
            print(message)  
            broadcast(received_bytes) 
        except Exception as e:
            print(f'something went wrong {e} received message')
            clients.remove(client)
            if clients:
                msg_dict = {'nickname': 'SERVER', 'message': f"{client.nickname} left the chat!"}
                broadcast_server_anouncements(pickle.dumps(msg_dict))
            client.socket.close()
            
            break
        finally:
            pass
    
def broadcast(message):
    for client in clients:
        try:
            print('broadcasting message')
            client.socket.send(message)
        except Exception as e:
            print(f"An error occurred: {e} broadcasting to {client.nickname}")


def broadcast_server_anouncements(message):
    for client in clients:
        try:
            print('broadcasting server announcment message')
            client.socket.send(message)
        except Exception as e:
            print(f"An error occurred: {e} broadcasting to {client.nickname}")

# function to receive connections from clients
def main():
    while True:
        # accept connection from client
        client_socket, address = server.accept()
        print(f"Connected with {str(address)}")
        
        # ask for nickname
        try:
            client_socket.send(b"NICK")  
            received_bytes = client_socket.recv(4096)
            nickname = pickle.loads(received_bytes)
            msg_dict = {'nickname': 'SERVER', 'message': f"{nickname} joined the chat!"}
            broadcast_server_anouncements(pickle.dumps(msg_dict))
        except Exception as e:
            print(f"An error occurred: {e} receiving nickname")
            client_socket.close()
            continue
            
        
        # create client object and add to clients list
        client = Client(client_socket, address, nickname)
        clients.append(client)

        # print status message on server terminal
        print (f"{address} belongs to {nickname}")

        # start thread to receive messages from client
        thread = threading.Thread(target=receive_messages, args=(client,))
        thread.start()

if __name__ == "__main__":
    print("Server is listening...")
    main()