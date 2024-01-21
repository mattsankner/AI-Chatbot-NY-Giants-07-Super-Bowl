# New York Giants 2007 Super Bowl Championship Run AI Chatbot

## Overview
This chatbot is a specialized AI assistant designed to provide detailed information about the New York Giants' 2007 Super Bowl Championship run. It is built using Python and incorporates various libraries to process and understand user queries, delivering relevant responses about players, games, and key moments from the championship run.

![Screenshot of my app](/assets/chatbotexample1.png)

## Features
- **Data-driven Responses:** Utilizes a structured JSON database (`datagiants.json`) containing sentences, contexts, keywords, and player info to provide accurate and context-specific information.
- **Natural Language Processing:** Employs NLTK and SpaCy for text processing, including tokenization, lemmatization, and keyword extraction, enhancing the chatbot's understanding of user queries.
- **Advanced Search Techniques:** Integrates TF-IDF Vectorization and cosine similarity measures to find the best match for user queries within the data.
- **Player Information Dictionary:** Contains detailed information about players and coaches, including roles, performance statistics, playoff highlights, and more.
- **GUI Interface:** Built using Tkinter, providing a user-friendly interface for interaction.

![Screenshot of my app](/assets/chatbotexample2.png)

## Manual Techniques Used
- **Preprocessing and Lemmatization:** Sentences from the JSON data are preprocessed and lemmatized for more effective matching.
- **Custom Keyword and Entity Extraction:** Manually crafted logic to extract relevant keywords and entities from sentences, improving the relevance of responses.
- **Question Type Identification:** Analyzes user queries to identify the type of question (e.g., 'who', 'what', 'when') for targeted searching.
- **Contextual Answering:** For player-specific queries, the bot retrieves tailored responses from the player info dictionary.
- **Repeated Query Detection:** Identifies and responds appropriately to repeated questions, enhancing user experience.

## Implementation Details
- **Python Libraries:** The application utilizes `json`, `nltk`, `spacy`, `re`, `tkinter`, `numpy`, and `sklearn` libraries.
- **Data Structure:** The `datagiants.json` file is structured with fields for sentences, contexts, keywords, entities, and question types, aiding in accurate data retrieval.
- **Player Info Dictionary:** A Python dictionary (`player_info`) that stores detailed information about the players and coaches.
- **User Input Processing:** The application processes user input for greetings, polite statements, repeated questions, and integrates a sophisticated method to search for answers or add new data.

![Screenshot of my app](/assets/chatbotexample1.png)

## Installation and Usage
1. **Dependencies:** Install the required Python libraries using `pip install nltk spacy numpy sklearn tkinter`.
2. **NLTK Data:** Download the necessary NLTK data (`wordnet`, `punkt`, `stopwords`).
3. **Running the Application:** Launch the chatbot by running `app.py`. The GUI will open for user interaction.
4. **Interacting with the Chatbot:** Type your queries related to the New York Giants' 2007 Super Bowl run in the chat window.

## Contribution
- **Adding Data:** The chatbot is designed to automatically process and integrate new data when a user enters a statement. The user can then query the statement entered.
