import datetime
import pickle

class Messages:
    def __init__(self, send_queue, receive_queue, client, nickname):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.client = client
        self.nickname = nickname
        self.now = datetime.datetime.now()
        
    def write_message(self) :
        while True:
            try:
                # Get message from queue True means block until item is available
                user_input = self.send_queue.get(block=True) 
                if user_input == '/quit':
                    self.client.close()
                    break
                msg_dict = {'nickname': self.nickname, 'message': user_input}
                message = pickle.dumps(msg_dict) # Encode message
                print(f"Sending message: {message}")
                self.client.send(message)    
            except Exception as e:
                print(f"An error occurred: {e}")
                self.client.close()
                break
            
    def receive_message(self):
        while True:
            try:
                received_bytes = self.client.recv(4096)
                try:
                    if b'NICK' in received_bytes:
                        self.client.send(pickle.dumps(self.nickname))
                    else:
                        message = pickle.loads(received_bytes)
                        sender_nickname = message['nickname']
                        message_content = message['message']
                        # Add message to queue
                        self.receive_queue.put(f"\n{self.now.strftime('%Y-%m-%d %H:%M:%S')} {sender_nickname}: {message_content}")
                except (UnicodeDecodeError, KeyError):
                    print("Error decoding message")
    
            except Exception as e:
                print(f"An error occurred: {e}")
                self.client.close()
                break
        
 
        