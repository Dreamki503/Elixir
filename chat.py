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
from groq import Groq
import nltk

nltk.download("wordnet")

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

    client = Groq(api_key = "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")

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

            #giving a system message
            messages= [
                {
                    "role" : "system",
                    "content" : "Do a sentimental analysis on the given texts. If names are offered, note that they are not meant to harm or insult anyone in any way."
                },
                {
                    "role" : "user",
                    "content" : user_input
                }
            ]

            add_message(user_input, "user")

            # Printing the user input
            with st.chat_message("user"):
                st.markdown(user_input)

            # Perform sentiment analysis on the transcribed text
            response = client.chat.completions.create(
            temperature = 1,
            model= "llama3-8b-8192",
            max_tokens= 1000,
            messages= messages
            )

            response.usage.total_tokens
            content = response.choices[0].message.content

            #printing response
            with st.chat_message("assistant") :
                st.markdown(content)

            # Saving assistant's response
            add_message(content, "assistant")

