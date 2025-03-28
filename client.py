#ASSIGNMENT 5
#NAME : DHIVYADHARSHINI KATHIRAVAN SATHYABAMA


import tkinter as tk
import requests
import json
import os
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path) as config_file:
        config = json.load(config_file)
    API_URL = config['api_url']
    THREAD_ID = config['thread_id']
except FileNotFoundError:
    messagebox.showerror("Error", "config.json file not found. Please create it in the same directory as client.py.")
    exit(1)
except KeyError as e:
    messagebox.showerror("Error", f"Missing key in config.json: {e}")
    exit(1)
except json.JSONDecodeError:
    messagebox.showerror("Error", "Invalid JSON format in config.json.")
    exit(1)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App")
        
        self.messages_frame = tk.Frame(self.root)
        self.messages_frame.pack()

        self.messages_text = ScrolledText(self.messages_frame, state='normal', width=50, height=20)
        self.messages_text.pack()

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack()

        self.input_field = tk.Entry(self.input_frame, width=40)
        self.input_field.pack(side=tk.LEFT)

        self.input_field.bind("<Return>", self.send_message_with_event)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT)

        self.populate_chat()

    def populate_chat(self):
        """Fetches the conversation history and displays it."""
        print(f"Thread ID: {THREAD_ID}, Populating screen with conversation history!")
        
        # Clear the chat window before populating
        self.messages_text.config(state='normal')
        self.messages_text.delete(1.0, tk.END)  # Clear all content
        self.messages_text.config(state='disabled')

        try:
            response = requests.get(f"{API_URL}/conversation-history/?thread_id={THREAD_ID}")
            if response.status_code == 200:
                data = response.json()
                self.messages_text.config(state='normal')
                for message in data['conversation_history']:
                    self.messages_text.insert(tk.END, f"{message['sender']}: {message['content']}\n")
                self.messages_text.config(state='disabled')

                
                self.messages_text.yview(tk.END)
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching conversation history: {e}")

    def send_message(self):
        """Sends a new message and updates the chat."""
        user_message = self.input_field.get()
        if user_message:
            # Display user message in the chat window
            self.messages_text.config(state='normal')
            self.messages_text.insert(tk.END, f"You: {user_message}\n")
            self.messages_text.config(state='disabled')
            self.input_field.delete(0, tk.END)

            # Send message to the API
            print(f"Thread ID: {THREAD_ID}, sending message: {user_message}")
            try:
                response = requests.post(f"{API_URL}/send-message/?thread_id={THREAD_ID}&message={user_message}")
                if response.status_code == 200:
                    assistant_response = response.json()["response"]
                    print(f"  Response: {assistant_response}")
                    self.messages_text.config(state='normal')
                    self.messages_text.insert(tk.END, f"Assistant: {assistant_response}\n")
                    self.messages_text.config(state='disabled')
                
                    # Scroll to the latest message
                    self.messages_text.yview(tk.END)
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending message: {e}")

    def send_message_with_event(self, event):
        """Wrapper to handle sending message when 'Enter' key is pressed."""
        self.send_message()

if __name__ == "__main__":
    root = tk.Tk()
    chat_app = ChatApp(root)
    root.mainloop()