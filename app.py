import streamlit as st
from streamlit_option_menu import option_menu
import chat, audio

# Set the page configuration first
st.set_page_config(page_title='Sentiment', initial_sidebar_state="collapsed")

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title="Menu",
                options=["Chat", "Audio"],
                icons=["chat-text-fill", "mic"],
                default_index=0,
                styles={
                    "icons": {"color": "white"}
                }
            )

        if app == "Chat":
            chat.app()

        if app == "Audio":
            audio.app()

# Create an instance of the MultiApp class
app = MultiApp()

# Add your apps
app.add_app("Chat", chat.app)
app.add_app("Audio", audio.app)

# Run the app
app.run()
