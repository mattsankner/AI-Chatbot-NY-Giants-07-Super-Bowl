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

#New addition
import random
    
prev_question = ""  # Add this at the start of your script

def reset_conversation():
    global prev_question
    prev_question = ""

def generate_angry_response():
    responses = [
        "I previously answered that question. Is there anything else I can help you with?",
        "Stop asking that! Can I answer something else?",
        "Stop messing with me... I am only trying to help! Ask a different question.",
        "I will not answer that again. Ask something different!",
        "Please try a different question, I already answered that."
    ]
    return random.choice(responses)

def generate_courtesy_response():
    responses = [
        "You are welcome! If you have any further questions, feel free to ask.",
        "No problem! Let me know if I can answer any other questions.",
        "Thanks for being polite. I am glad I could help.",
        "I am here to help! Let me know if I can be of any other assistance to you.",
        "You got it!",
        "Absolutely, let me know if you need anything else from me."
    ]
    return random.choice(responses)


# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the lemmatizer and SpaCy
lemmatizer = WordNetLemmatizer()
nlp = spacy.load("en_core_web_sm")

#Preprocess and Lemmatize the sentences
def preprocess_and_lemmatize(data):
    # Updated to include new JSON fields
    sentences = []
    for entry in data['data']:
        sentence = entry['sentence']
        context = entry.get('context', '')
        keywords = ' '.join(entry.get('keywords', []))
        combined_text = f"{sentence} {context} {keywords}"
        sentences.append(combined_text)
    return [" ".join([lemmatizer.lemmatize(word.lower()) for word in word_tokenize(sentence)]) for sentence in sentences]

# Load the JSON data
# This function reads data from a JSON file
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Load data and initialize TF-IDF Vectorizer
data = load_data('nygiants.json')
preprocessed_data = preprocess_and_lemmatize(data)
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_data)

def extract_query_info(query):
    for player in player_info:
        if player.lower() in query.lower():
            if any(word in query.lower() for word in ["highlight", "highlights", "pinnacle", "best play", "memorable"]):
                return "highlights", player
            elif any(word in query.lower() for word in ["playoffs", "postseason", "playoff"]):
                return "playoffs_performance", player
            elif any(word in query.lower() for word in ["performance", "perform", "stats", "stat", "season", "game", "match", "how"]):
                return "regular_performance", player
            else:
                return "role", player

    return "general", None

def is_who_question(query):
    return 'who' in query.lower().split()

def find_best_match(query, data):
    query_type, entity = extract_query_info(query)

    if entity in player_info:
        if query_type == "highlights":
            return player_info[entity].get("highlights", "No specific highlights data available.")
        elif query_type == "playoffs_performance":
            return player_info[entity].get("playoffs", "No specific playoffs data available.")
        elif query_type == "regular_performance":
            return player_info[entity].get("performance", "No specific performance data available.")
        else:
            return f"{entity} was a {player_info[entity]['role']} for the New York Giants."

    elif is_who_question(query):
        return handle_who_question(query, data)

    else:
        return search_with_tf_idf(query, data)

    
def handle_who_question(query, data):
    query_tokens = set(word_tokenize(query.lower()))
    best_match = None
    highest_score = 0

    print("Considering sentences for 'Who' question:")

    for entry in data['data']:
        if 'who' in entry.get('question_type', []):
            sentence_entities = entry.get('entities', [])
            score = sum(token in query_tokens for token in sentence_entities)

            print(f"Sentence: \"{entry['sentence']}\", Score: {score}, Entities: {sentence_entities}")

            if score > highest_score:
                highest_score = score
                best_match = entry['sentence']

    if best_match:
        return best_match
    else:
        return "I'm sorry, I don't have information on that."

def search_with_tf_idf(query, data):
    # Preprocess the query
    query_processed = " ".join([lemmatizer.lemmatize(word.lower()) for word in word_tokenize(query)])
    query_tfidf = tfidf_vectorizer.transform([query_processed])

    # Calculate cosine similarities between the query and each sentence in the JSON data
    cosine_similarities = np.dot(query_tfidf, tfidf_matrix.T).toarray()[0]

    # Sort the sentences based on similarity scores
    sorted_indices = np.argsort(cosine_similarities)[::-1]

    # Retrieve and print the top three sentences for debugging
    top_sentences = []
    for index in sorted_indices[:3]:
        sentence = data['data'][index]['sentence']
        top_sentences.append((sentence, cosine_similarities[index]))
        print(f"Sentence: \"{sentence}\", Similarity Score: {cosine_similarities[index]}")

    # Return the sentence with the highest score
    best_match_index = sorted_indices[0]
    if cosine_similarities[best_match_index] > 0.2:  # Threshold for relevance
        return top_sentences[0][0]  # Return the full sentence
    return "I'm sorry, I don't have information on that."

# Save the JSON data
def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Process and add new data to JSON
def add_new_data(sentence, data):
    # This function now extracts keywords and question words more effectively
    doc = nlp(sentence)
    new_entry = {
        "sentence": sentence,
        "keywords": [token.text for token in doc if token.is_alpha and not token.is_stop],
        "question_words": [token.text for token in doc if token.text.lower() in question_indicators]
    }
    data['data'].append(new_entry)
    save_data('nygiants.json', data)  # Assuming you want to save to the file immediately
    return "New information added: " + sentence


# Extract keywords from a sentence
def extract_keywords(sentence):
    # Custom logic to extract more relevant keywords
    doc = nlp(sentence)
    # Example: Extract Named Entities and Noun Phrases
    entities = [ent.text for ent in doc.ents]
    noun_phrases = [np.text for np in doc.noun_chunks]
    return entities + noun_phrases

# Placeholder for extracting question words (needs a more sophisticated implementation)
def extract_question_words(sentence):
    # Basic implementation, this should be expanded
    return ["Who", "What", "When", "Where", "Why", "How"]

question_indicators = [
    "who", "what", "when", "where", "why", "how", 
    "is", "can", "does", "do", "are", "will", 
    "shall", "should", "would", "could", "may", "might", "tell me", 
    "tell", "show me", "show", "give me", "give", "explain", "describe", 
    "list", "name", "define", "state", "mention", "identify", "provide", "write", 
    "say", "speak", "talk", "discuss", "present", "outline", "summarize", "compare", 
    "contrast", "differentiate", "distinguish", "analyze", "evaluate", "assess", 
    "critique", "justify", "argue", "prove", "demonstrate", "solve", "calculate", 
    "determine", "find", "measure", "draw", "sketch", "construct", "design", "plan", 
    "create", "compose", "organize", "formulate", "develop", "prepare", "propose", 
    "recommend", "suggest", "improve", "revise", "modify", "adapt", "adjust", "refine", 
    "reframe", "refactor", "reorganize", "restructure", "rethink", "reconsider", "reassess", 
    "re-evaluate", "re-examine", "revisit", "rework", "rewrite", "rephrase", "reword", "restate", 
    "reformulate", "recreate", "rebuild", "reconstruct", "reinvent", "reproduce", "de-construct"
]

def process_input(user_input, data):
    global prev_question

    # Normalize input for consistency
    normalized_input = user_input.lower().strip()

    # Check if it's a greeting
    if normalized_input == 'hello':
        return "Hello! I am your New York Football Giant's 2007 SuperBowl Run Chat Assistant! How can I help you today?"

    # Check for polite statements
    polite_words = ["please", "thank you", "thanks", "appreciate it"]
    if any(polite_word in normalized_input for polite_word in polite_words):
        reset_conversation()
        return generate_courtesy_response()

    # Check for repeated questions
    if normalized_input == prev_question:
        return generate_angry_response()

    # Save the current question for comparison in the next interaction
    prev_question = normalized_input

    # If the input is a question, search for an answer
    if normalized_input.endswith('?') or normalized_input.split()[0] in question_indicators:
        return search_data(user_input, data)
    
    # If the input is not a question, treat it as new data to add
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
