import socket
import threading
import tkinter as tk
from queue import Queue
import datetime
import pickle

height = 600
width = 600
primewindow = tk.Tk()
primewindow.title("Chatroom")
primewindow.geometry(f"{width}x{height}")

chatBox = tk.Text(primewindow, height=20, width=60)
chatBox.pack()
userInput = tk.Entry(primewindow, width=45)  # Changed to Entry for single-line input
userInput.pack(side=tk.BOTTOM)

sendbutton = tk.Button(primewindow, text="Send" )
sendbutton.pack(side=tk.RIGHT)

# function to send nickname to server
def send_nickname_to_server(client, nickname):
    client.sendall(pickle.dumps(nickname))

# function to receive messages from server and display them in chatBox
def receive_message():
      while True:
        try:
            received_bytes = client.recv(4096)
            try:
                if b'NICK' in received_bytes:
                    send_nickname_to_server(client, nickname)
                else:
                    message = pickle.loads(received_bytes)
                    sender_nickname = message['nickname']
                    message_content = message['message']
                    
                    # Add message to queue
                    received_message_queue.put(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} {sender_nickname}: {message_content}")
                    print(received_message_queue.qsize())
            except (UnicodeDecodeError, KeyError):
                print("Error decoding message")

        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break


def write_message():
    while True:
        try:
            user_input = input("Me: ")
            msg_dict = {'nickname': nickname, 'message': user_input}
            message = pickle.dumps(msg_dict) # Encode message
            
            # Send message size and message to server
            client.send(message)
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

def update_chatBox_window():
    while True:
        try:
            (received_message_queue.qsize())
            message = received_message_queue.get(block=False) # Get message from queue
            chatBox.config(state='normal') # Allow writing to chatBox
            chatBox.insert('end', message) # Write message to chatBox
            chatBox.see(tk.END)  # Scroll if necessary
            chatBox.config(state='disabled') # Disable writing to chatBox
            primewindow.update_idletasks()  # Force an update of the GUI to display the message
        except Exception as e:
            #print(f"An error occurred: {e}")
            pass

def opening_socket(HOST, PORT):
    try:
        print(f"Connecting to {HOST} on port {PORT}")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket
        client.connect((HOST, PORT)) # Connect to server
        print(f"Connected to {HOST} on port {PORT}")
        return client
    except Exception as e:
        print(f"An error occurred: {e}")
        client.close()
        return None



if __name__ == '__main__':
    # Set up socket
    HOST = '127.0.0.1'
    PORT = 65432    
    
    # Queue to communicate between threads
    received_message_queue = Queue()
    send_message_queue = Queue()

    # Get current time
    now = datetime.datetime.now()

    # Get nickname
    nickname = input("Choose your nickname: ")
    client = opening_socket(HOST, PORT)

    # Start threads
    receive_thread = threading.Thread(target=receive_message) # create thread for receiving messages
    receive_thread.start()
    
    update_thread = threading.Thread(target=update_chatBox_window) # create thread for updating chatBox
    update_thread.start()
    
    write_thread = threading.Thread(target=write_message) # create thread for writing messages
    write_thread.start()


# !TODO: Add GUI as a thread and own function
    primewindow.mainloop() # Start GUI
