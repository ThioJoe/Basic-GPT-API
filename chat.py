import openai
import json
import tkinter as tk
import datetime
import os
from tkinter import scrolledtext

model = "gpt-4"
systemPrompt = "You are a helpful assistant."

# Create 'Chat Logs' directory if it does not exist
if not os.path.exists('Chat Logs'):
    os.makedirs('Chat Logs')
    
# Create 'Saved Chats' directory if it does not exist
if not os.path.exists('Saved Chats'):
    os.makedirs('Saved Chats')    

# ----------------------------------------------------------------------------------

# Load API key from key.txt file
def load_api_key(filename="key.txt"):
    try:
        with open(filename, "r", encoding='utf-8') as key_file:
            for line in key_file:
                stripped_line = line.strip()
                if not stripped_line.startswith('#') and stripped_line != '':
                    api_key = stripped_line
                    break
        return api_key
    except FileNotFoundError:
        print("\nAPI key file not found. Please create a file named 'key.txt' in the same directory as this script and paste your API key in it.\n")
        exit()

openai.api_key = load_api_key()

# Generate the filename only once when the script starts
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = os.path.join('Chat Logs', f'log_{timestamp}.txt')

def send_and_receive_message(userMessage, messagesTemp, temperature=0.5):
    messagesTemp.append({"role": "user", "content": userMessage})

    chatResponse = openai.ChatCompletion.create(
        model=model,
        messages=messagesTemp,
        temperature=temperature
        )
    
    chatResponseMessage = chatResponse.choices[0].message.content
    chatResponseRole = chatResponse.choices[0].message.role

    print("\n" + chatResponseMessage)

    messagesTemp.append({"role": chatResponseRole, "content": chatResponseMessage})

    # Write chat history to the log file
    with open(log_file_path, 'a', encoding='utf-8') as log_file:  # Notice 'a' for append mode
        # Write the user message and the assistant response, capitalizing the role
        log_file.write(f"{messagesTemp[-2]['role'].capitalize()}: {messagesTemp[-2]['content']}\n\n")  # Extra '\n' for blank line
        log_file.write(f"    {messagesTemp[-1]['role'].capitalize()}: {messagesTemp[-1]['content']}\n\n")  # Indent assistant entries

    return messagesTemp

def check_special_input(text):
    if text == "file":
        text = get_text_from_file()
    elif text == "clear":
        text = clear_conversation_history()
    elif text == "save":
        text = save_conversation_history()
    elif text == "load":
        text = load_conversation_history()
    elif text == "switch":
        text = switch_model()
    elif text == "temp":
        text = set_temperature()
    elif text == "box":
        text = get_multiline_input()
    elif text == "exit":
        exit_script()
    return text

def get_text_from_file():
    path = input("\nPath to the text file contents to send: ")
    path = path.strip('"')
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

def clear_conversation_history():
    global messages
    messages = [{"role": "system", "content": systemPrompt}]
    print("\nConversation history cleared.")
    return ""

def save_conversation_history():
    filename = input("\nEnter the file name to save the conversation: ")
    save_path = os.path.join('Saved Chats', filename)
    with open(save_path, "w", encoding="utf-8") as outfile:
        json.dump(messages, outfile, ensure_ascii=False, indent=4)
    print(f"\nConversation history saved to {save_path}.")
    return ""

def load_conversation_history():
    filename = input("\nEnter the file name to load the conversation: ")
    load_path = os.path.join('Saved Chats', filename)
    global messages
    with open(load_path, "r", encoding="utf-8") as infile:
        messages = json.load(infile)
    print(f"\nConversation history loaded from {load_path}.")
    return ""

def switch_model():
    global model
    new_model = input("\nEnter the new model name (e.g., 'gpt-4', 'gpt-3', etc.): ")
    model = new_model
    print(f"\nModel switched to {model}.")
    return ""

def set_temperature():
    global temperature
    temp = float(input("\nEnter a temperature value between 0 and 1 (default is 0.5): "))
    temperature = temp
    print(f"\nTemperature set to {temperature}.")
    return ""

def exit_script():
    print("\nExiting the script. Goodbye!")
    exit()


def get_multiline_input():
    def submit_text():
        nonlocal user_input
        user_input = text_box.get("1.0", tk.END)
        root.quit()

    user_input = ""
    root = tk.Tk()
    root.title("Multi-line Text Input")

    # Set the initial window size
    root.geometry('450x300')

    # Create a scrolled text widget
    text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_box.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=submit_text)
    submit_button.grid(row=1, column=0, pady=5)

    # Configure the grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
    root.destroy()

    return user_input.strip()

messages = [{"role": "system", "content": systemPrompt}]
temperature = 0.5

# Print list of special commands and description
print("---------------------------------------------")
print("\nBegin the chat by typing your message and hitting Enter. Here are some special commands you can use:\n")
print("  file:   Send the contents of a text file as your message. It will ask you for the file path of the file.")
print("  box:    Send the contents of a multi-line text box as your message. It will open a new window with a text box.")
print("  clear:  Clear the conversation history.")
print("  save:   Save the conversation history to a file.")
print("  load:   Load the conversation history from a file.")
print("  switch: Switch the model.")
print("  temp:   Set the temperature.")
print("  exit:   Exit the script.\n")


while True:
    userEnteredPrompt = input("\n >>>    ")
    userEnteredPrompt = check_special_input(userEnteredPrompt)
    if userEnteredPrompt:
        print("----------------------------------------------------------------------------------------------------")
        messages = send_and_receive_message(userEnteredPrompt, messages, temperature)
