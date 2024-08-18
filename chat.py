import streamlit as st
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import re
import os

if "load" not in st.session_state:
    st.session_state.load = False

if st.session_state.load : 
    nltk.download('punkt')
    nltk.download('stopwords')
    st.session_state.load = True

# Function to load positive and negative words
def load_words(file_path):
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return set(file.read().split())
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Could not decode file {file_path} with available encodings.")

# Load positive and negative words
positive_words = load_words('assests/Negative words.docx')
negative_words = load_words('assests/Positive words.docx')
# Load stop words
stop_words_dir = 'assests/stopwords'
stop_words = set()
for filename in os.listdir(stop_words_dir):
    with open(os.path.join(stop_words_dir, filename), 'r', encoding='latin1') as file:
        stop_words.update(file.read().split())

# Function to clean and tokenize text
def clean_text(text):
    words = word_tokenize(text)
    cleaned_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    return cleaned_words

# Function to count syllables in a word
def syllable_count(word):
    word = word.lower()
    vowels = "aeiou"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if word.endswith("es") or word.endswith("ed"):
        count -= 1
    if count == 0:
        count += 1
    return count

# Function to analyze text
def analyze_text(text):
    sentences = sent_tokenize(text)
    words = clean_text(text)

    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words) * -1

    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)

    avg_sentence_length = len(words) / len(sentences) if len(sentences) > 0 else 0

    complex_words = [word for word in words if syllable_count(word) > 2]
    percentage_complex_words = len(complex_words) / len(words) * 100 if len(words) > 0 else 0

    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    avg_words_per_sentence = len(words) / len(sentences) if len(sentences) > 0 else 0
    complex_word_count = len(complex_words)
    word_count = len(words)

    syllables = sum(syllable_count(word) for word in words)
    syllable_per_word = syllables / len(words) if len(words) > 0 else 0

    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))

    avg_word_length = sum(len(word) for word in words) / len(words) if len(words) > 0 else 0

    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllable_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length,
    }

def analyze_sentiment(text):
    # Create a TextBlob object
    blob = TextBlob(text)
    
    # Determine the polarity
    polarity = blob.sentiment.polarity
    
    # Classify the sentiment based on polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Function to extract article text
def extract_article_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assuming the article title is in <h1> tag and text is in <p> tags
        title = soup.find('h1').get_text()
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])

        return title + '\n' + article_text
    except Exception as e:
        return f"Error extracting {url}: {e}"

# Function to check if input is a valid URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def app():
    st.title("Sentimental Analysis :green[Text]")
    st.subheader("Enter a text or link to analyze")
    st.divider()

    # Initializing a session state to store previous conversations
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Printing previous conversations
    for message in st.session_state.messages: 
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Function to save user and assistant messages
    def add_message(content, role="user"):
        st.session_state.messages.append({"role": role, "content": content})
    
    # Prompt user for input
    user_input = st.chat_input("Enter something")
    
    if user_input:
        if is_valid_url(user_input):
            # If the input is a valid URL, extract and display the article text
            article_text = extract_article_text(user_input)
            add_message(user_input, "user")
            
            #printing user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            #Analyzing text
            sentiment = analyze_sentiment(article_text)
            output = f"The text is {sentiment}"
            # st.write(sentiment)
            
            # printing assistant message
            with st.chat_message("assistant"):
                st.markdown(output)  
            
            # Saving assistant's response
            add_message(output, "assistant")

        else:
            # Saving user input
            add_message(user_input, "user")

            # Printing the user input
            with st.chat_message("user"):
                st.markdown(user_input)

            # Analyze the sentiment of the input text
            sentiment = analyze_text(user_input)
            output = f"The text is {sentiment}"

            # Print the result
            with st.chat_message("assistant"):
                st.markdown(output)

            # Saving assistant's response
            add_message(output, "assistant")

