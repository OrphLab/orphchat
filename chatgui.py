import tkinter as tk

class PrimaryWindow:
    def __init__(self, master, send_queue, receive_queue):
        self.master = master
        self.master.title("Chatroom")
        self.master.geometry("600x600")
        self.master.resizable(False, False)
        
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        
        self.chatBox = tk.Text(self.master, height=20, width=60)
        self.chatBox.pack()
        
        self.userInput = tk.Entry(self.master, width=45)
        self.userInput.pack(side=tk.BOTTOM)
        
        self.sendbutton = tk.Button(
            self.master,
            text="Send",
            command=lambda: (self.send_queue.put(self.userInput.get()),
                             self.userInput.delete(0, tk.END))
        )
        self.sendbutton.pack(side=tk.RIGHT)
        
    def nickname_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Nickname")
        popup.geometry("300x100")
        popup.resizable(False, False)
        
        entry = tk.Entry(popup)
        entry.pack()
        
        def get_input():
            user_input = entry.get()
            print(f"User input: {user_input}")
            self.send_queue.put(user_input)
            popup.destroy()
            
        cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
        cancel_button.pack()
            
        ok_button = tk.Button(popup, text="OK", command=get_input)
        ok_button.pack()
        
    def update_chatBox_window(self):
        while True:
            try:
                message = self.receive_queue.get(block=False) # Get message from queue
                self.chatBox.config(state='normal') # Allow writing to chatBox
                self.chatBox.insert('end', message) # Write message to chatBox
                self.chatBox.see(tk.END)  # Scroll if necessary
                self.chatBox.config(state='disabled') # Disable writing to chatBox
            except Exception as e:
                #print(f"An error occurred: {e}")
                pass
                
        
        
