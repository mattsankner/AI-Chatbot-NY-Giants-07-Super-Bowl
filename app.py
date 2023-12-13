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
    # Iterate through each player in player_info
    for player in player_info:
        if player.lower() in query.lower():

             # Check for keywords related to highlights
            if any(word in query.lower() for word in ["highlight", "highlights", "known for", "pinnacle", "best", "best play", "memory", "memorable", "notable", "famous", "iconic"]):
                return "highlights", player
            
            # Check for keywords related to performance
            if any(word in query.lower() for word in ["statistics", "performance", "perform", "stats","stat","how did", "how was","how would", "play", "played", "plays", "playing", "game", "games", "gameday", "gamedays", "match", "matches", "matched", "matching", "season", "seasons", "how"]):
                
                # Check for keywords related to playoffs
                if any(playoff_word in query.lower() for playoff_word in ["playoffs", "post-season","postseason", "post-season", "postseasons", "post-seasons", "postseason's", "post-season's", "postseasons'", "post-seasons'", "postseasons's", "post-seasons's"]):
                    return "playoffs_performance", player
                return "regular_performance", player

            # Default to role if no specific keyword is found
            return "role", player

    # Handle general info queries
    general_info_pattern = r"(?i)\btell me about\b\s*([\w\s']+)"
    general_info_match = re.search(general_info_pattern, query)
    if general_info_match:
        return "general_info", general_info_match.group(1).strip()

    return "general", None



def find_best_match(query, data):
    query_type, entity = extract_query_info(query)

    # Respond with player's highlights information
    if query_type == "highlights" and entity in player_info:
        highlights_info = player_info[entity].get("highlights", "No specific highlights data available.")
        return highlights_info
    
    # Respond with player's regular season performance information
    if query_type == "regular_performance" and entity in player_info:
        performance_info = player_info[entity].get("performance", "No specific performance data available.")
        return performance_info

    # Respond with player's playoffs performance information
    if query_type == "playoffs_performance" and entity in player_info:
        playoffs_info = player_info[entity].get("playoffs", "No specific playoffs data available.")
        return playoffs_info

    # Respond with player's role
    if query_type == "role":
        return f"{entity} was a {player_info[entity]['role']} for the New York Giants."

    # Handle general info queries
    if query_type == "general_info" and entity in player_info:
        role_info = player_info[entity].get("role", "")
        performance_info = player_info[entity].get("performance", "")
        return f"{entity} was a {role_info} for the New York Giants. {performance_info}"

    # Fallback to TF-IDF for other queries
    return search_with_tf_idf(query, data)

def search_with_tf_idf(query, data):
    # Process query for TF-IDF comparison
    query_processed = " ".join([lemmatizer.lemmatize(word.lower()) for word in word_tokenize(query)])
    query_tfidf = tfidf_vectorizer.transform([query_processed])
    cosine_similarities = np.dot(query_tfidf, tfidf_matrix.T).toarray()[0]
    best_match_index = np.argmax(cosine_similarities)

    # Check if a relevant match is found
    if cosine_similarities[best_match_index] > 0.2:  # Adjusted threshold
        return data['data'][best_match_index]['sentence']
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
    save_data('giants.json', data)  # Assuming you want to save to the file immediately
    return "New information added: " + sentence



#introduced normalized_input to handle the case insensitivity and trimming of the user input.
#I kept the checks for greeting and polite statements at the top since they should override other types of input.
#I added a check for repeated questions using the prev_question global variable.
#After all checks, the function determines whether the input is a question or a new data statement based on the presence of a question mark or question indicators.
#If it's a question, the search_data function is called; otherwise, the add_new_data function is called.


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
