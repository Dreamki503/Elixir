import io
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from textblob import TextBlob
import nltk
from groq import Groq

nltk.download("wordnet")

# Initialize floating elements if needed
from streamlit_float import *
float_init()

def speech_to_text(audio_bytes):
    """Convert audio bytes to text using SpeechRecognition."""
    recognizer = sr.Recognizer()

    # Convert the audio bytes into an AudioFile object
    audio_file = sr.AudioFile(io.BytesIO(audio_bytes))

    with audio_file as source:
        audio = recognizer.record(source)

    try:
        # Recognize the speech in the audio
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from the speech recognition service; {e}"

def analyze_sentiment(text):
    """Analyze the sentiment of the provided text using TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def app():
    st.title("Sentimental Analysis :green[Audio]")
    st.divider()

    # Create a footer container for the microphone
    footer_container = st.container()
    with footer_container:
        # Record audio
        audio_bytes = audio_recorder()

        if audio_bytes:
            # Convert audio bytes to text
            text = speech_to_text(audio_bytes)
            
            if text:
                if text == "Sorry, I could not understand the audio." :
                    with st.chat_message("assistant"):
                        st.markdown(text + " Please try again.")
                
                else:
                    #giving a system message
                    messages= [
                        {
                            "role" : "system",
                            "content" : "Do a sentimental analysis on the given texts. If names are offered, note that they are not meant to harm anyone. "
                        },
                        {
                            "role" : "user",
                            "content" : text
                        }
                    ]

                    # Display the transcribed text
                    with st.chat_message("user") :
                        st.markdown(text)
                    
                    client = Groq(api_key = "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")
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
