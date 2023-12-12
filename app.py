import json
import nltk
import spacy
import re
import tkinter as tk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from playerinfo import player_info

# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the lemmatizer and SpaCy
lemmatizer = WordNetLemmatizer()
nlp = spacy.load("en_core_web_sm")

#Preprocess and Lemmatize the sentences
def preprocess_and_lemmatize(data):
    sentences = [entry['sentence'] for entry in data['data']]
    return [" ".join([lemmatizer.lemmatize(word.lower()) for word in word_tokenize(sentence)]) for sentence in sentences]

# Load the JSON data
# This function reads data from a JSON file
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Load data and initialize TF-IDF Vectorizer
data = load_data('giants.json')
preprocessed_data = preprocess_and_lemmatize(data)
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_data)

# Regex pattern to extract information from queries
def extract_query_info(query):
    role_pattern = r"(?i)\b(?:what (?:position|role) (?:does|did)|who (?:is|was|are|were))\b\s*([\w\s']+)"
    general_info_pattern = r"(?i)\btell me about\b\s*([\w\s']+)"
    
    for pattern, query_type in [(role_pattern, "role"), (general_info_pattern, "general_info")]:
        match = re.search(pattern, query)
        if match:
            return query_type, match.group(1).strip()

    return "general", None


def find_best_match(query, data):
    query_type, entity = extract_query_info(query)
    
    if query_type == "role" and entity in player_info:
        return f"{entity} was a {player_info[entity]['role']} for the New York Giants."

    if query_type == "general_info" and entity in player_info:
        role_info = player_info[entity].get("role", "No specific role data available.")
        performance_info = player_info[entity].get("performance", "")
        return f"{entity} was a {role_info} for the New York Giants. {performance_info}"

    if query_type == "action" and entity in player_info:
        action_info = player_info[entity].get("performance", "No specific action data available.")
        return action_info

    if query_type == "group":
        players = [player for player, info in player_info.items() if info['role'].startswith(entity.lower())]
        if players:
            return f"{', '.join(players)} were the {entity.lower()} for the New York Giants."
        else:
            return search_with_tf_idf(query, data)

    return search_with_tf_idf(query, data)

def search_with_tf_idf(query, data):
    # Process query for TF-IDF comparison
    query_processed = " ".join([lemmatizer.lemmatize(word.lower()) for word in word_tokenize(query)])
    query_tfidf = tfidf_vectorizer.transform([query_processed])
    cosine_similarities = np.dot(query_tfidf, tfidf_matrix.T).toarray()[0]
    best_match_index = np.argmax(cosine_similarities)

    # Check if a relevant match is found
    if cosine_similarities[best_match_index] > 0.1:
        return data['data'][best_match_index]['sentence']
    return "I'm sorry, I don't have information on that."

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
    doc = nlp(sentence)
    entities = [ent.text for ent in doc.ents]
    return entities if entities else [word.lower() for word in word_tokenize(sentence) if word.isalpha()]

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

# Updated search_data function
def search_data(query, data):
    return find_best_match(query, data)


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
