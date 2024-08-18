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
            sentiment = analyze_sentiment(user_input)
            output = f"The text is {sentiment}"

            # Print the result
            with st.chat_message("assistant"):
                st.markdown(output)

            # Saving assistant's response
            add_message(output, "assistant")

