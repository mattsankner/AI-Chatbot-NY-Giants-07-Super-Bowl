import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')
import tkinter as tk

# Load the JSON data
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Save the JSON data
def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Process and add new data to JSON
def add_new_data(sentence, data):
    # This function needs to be expanded based on your data structure and needs
    # Here is a basic implementation
    new_entry = {
        "sentence": sentence,
        "keywords": extract_keywords(sentence),
        "question_words": extract_question_words(sentence)
    }
    data['data'].append(new_entry)
    return "New information added: " + sentence

# Extract keywords from a sentence
def extract_keywords(sentence):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(sentence)
    keywords = [word for word in word_tokens if word.lower() not in stop_words]
    return keywords

# Placeholder for extracting question words (needs a more sophisticated implementation)
def extract_question_words(sentence):
    # Basic implementation, this should be expanded
    return ["Who", "What", "When", "Where", "Why", "How"]

# Process user input
def process_input(user_input, data):
    # Check if the input is a question or a statement to add data
    if "?" in user_input or user_input.endswith('.'):
        return search_data(user_input, data)
    else:
        return add_new_data(user_input, data)

# Search for an answer in the data (basic implementation, needs to be improved)
def search_data(query, data):
    keywords = extract_keywords(query)
    print(f"Query Keywords: {keywords}")
    
    # General matching
    best_match = None
    max_keyword_matches = 0

    for entry in data['data']:
        matched_keywords = [keyword for keyword in keywords if keyword.lower() in entry['sentence'].lower()]
        keyword_match_count = len(matched_keywords)

        if keyword_match_count > max_keyword_matches:
            max_keyword_matches = keyword_match_count
            best_match = entry['sentence']

    if max_keyword_matches > 1:  # Adjust the threshold as needed
        return best_match
    return "I'm sorry, I don't have information on that."


# Example usage within the GUI
def send_message(event=None):
    msg = my_message.get()
    if msg.strip() != "":
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "You: " + msg + "\n")
        response = process_input(msg, data)
        bot_response(response)
        chat_window.config(state=tk.DISABLED)
        my_message.set("")

# Load data
data = load_data('giants.json')

# Rest of GUI code...
root = tk.Tk()
root.title("Simple Virtual Assistant")
root.geometry("690x635")


def bot_response(response):
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, "Agent: " + response + "\n")
    chat_window.config(state=tk.DISABLED)
    
chat_window = tk.Text(root, width=60, height=30, font=('Verdana', 15))
chat_window.config(state=tk.DISABLED)
chat_window.grid(row=0, column=0, columnspan=2, padx=15, pady=15)


my_message = tk.StringVar()
entry_field = tk.Entry(root, textvariable=my_message, width= 48, font=('Verdana',
15))
entry_field.grid(row=1, column=0)
entry_field.bind("<Return>", send_message)

send_button = tk.Button(root, text="Send", command=send_message, width=6)
send_button.grid(row=1, column=1)

topic = 'NY Giants 2007 SuperBowl Championship Run'
initial_response = "Hi, I am your virtual assistant, ask me anything about the " + topic

bot_response(initial_response)
root.mainloop()
