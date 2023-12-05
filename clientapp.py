import socket
import threading
import tkinter as tk
from queue import Queue
import datetime
import pickle
from chatmessages import Messages
from chatgui import PrimaryWindow

# function to send nickname to server
def send_nickname_to_server(client, nickname):
    client.sendall(pickle.dumps(nickname))

# function to receive messages from server and display them in chatBox
# it takes the message from the server and puts it in the queue, unless the msg
# is  NICK, in which case it sends the nickname to the server
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
                    #print(received_message_queue.qsize())
            except (UnicodeDecodeError, KeyError):
                print("Error decoding message")

        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

# function to send messages to server
# it takes user input from the queue and sends it to the server
def write_message(user_input_queue):
    while True:
        try:
            user_input = user_input_queue.get(block=True)
            # TODO: make this work at scale
            if user_input == '/quit':
                client.close()
                break
            msg_dict = {'nickname': nickname, 'message': user_input}
            message = pickle.dumps(msg_dict) # Encode message

            client.send(message)
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

# function to open socket
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

# function to create GUI
def gui_primary_window():
    try:
        height = 600
        width = 600
        prime_window = tk.Tk()
        nickname_popup(prime_window)
        prime_window.title("Chatroom")
        prime_window.geometry(f"{width}x{height}")

        global chatBox
        chatBox = tk.Text(prime_window, height=20, width=60)
        chatBox.pack() #packs the chatBox into the window and displays it

        userInput = tk.Entry(prime_window, width=45)
        userInput.pack(side=tk.BOTTOM)

        sendbutton = tk.Button(
                prime_window,
                text="Send",
                command=lambda: (user_input_queue.put(userInput.get()), 
                                 userInput.delete(0, tk.END))
                                )
        
        sendbutton.pack(side=tk.RIGHT)
        
        prime_window.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        client.close()
        return None
        
def nickname_popup(prime_window):
    popup = tk.Toplevel(prime_window)
    popup.title("Nickname")
    popup.geometry("300x100")
    popup.resizable(False, False)
    
    entry = tk.Entry(popup)
    entry.pack()
    
    def get_input():
        user_input = entry.get()
        print(f"User input: {user_input}")
        user_input_queue.put(user_input)
        popup.destroy()
        
    cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
    cancel_button.pack()
        
    ok_button = tk.Button(popup, text="OK", command=get_input)
    ok_button.pack()
    

    popup.wait_window()

# function to update chatBox window
def update_chatBox_window():
    while True:
        try:
            message = received_message_queue.get(block=False) # Get message from queue
            chatBox.config(state='normal') # Allow writing to chatBox
            chatBox.insert('end', message) # Write message to chatBox
            chatBox.see(tk.END)  # Scroll if necessary
            chatBox.config(state='disabled') # Disable writing to chatBox
        except Exception as e:
            #print(f"An error occurred: {e}")
            pass

# main function
if __name__ == '__main__':
    # Set up socket
    HOST = '127.0.0.1'
    PORT = 65432    
    
    # Queue to communicate between threads
    received_message_queue = Queue()
    user_input_queue = Queue()
    master = tk.Tk()
    
    chatgui= PrimaryWindow(master, user_input_queue, received_message_queue)
    
    # Get current time
    now = datetime.datetime.now()

    # Get nickname
    nickname = input("Choose your nickname: ") #! this should be a popup window
    client = opening_socket(HOST, PORT)
    chatmessages = Messages(user_input_queue, received_message_queue, client, nickname)

    # Start threads
    print('starting threads - receive')
    receive_thread = threading.Thread(target=chatmessages.receive_message) # create thread for receiving messages
    receive_thread.start()
    
    print('starting threads - update')
    update_thread = threading.Thread(target=chatgui.update_chatBox_window) # create thread for updating chatBox
    update_thread.start()
    
    print('starting threads - write')
    write_thread = threading.Thread(target=chatmessages.write_message) # create thread for writing messages
    write_thread.start()

    #gui_thread = threading.Thread(target=chatgui)
    #gui_thread.start()
    
    print('threads started')

    master.mainloop()
    
   # TODO: Add windows promopt for nickname
   # TODO: Figure out new logi for updateing chatpox window, and delete global chatbox variable 
