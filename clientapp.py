import socket
import threading
import tkinter as tk
from queue import Queue
import datetime
from chatmessages import Messages
from chatgui import PrimaryWindow

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
        
# main function
if __name__ == '__main__':
    # Set up socket
    HOST = '127.0.0.1'
    PORT = 65432    
    
    # Queue to communicate between threads
    received_message_queue = Queue()
    user_input_queue = Queue()
    
    # Create GUI window
    master = tk.Tk()
    
    # Create GUI object
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

    print('threads started')

    master.mainloop()
    
   # TODO: Add windows promopt for nickname
   
