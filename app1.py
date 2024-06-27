import streamlit as st
from openai import OpenAI
from tools import Tools
import json
import time

# Initialize OpenAI client (ensure you have the correct API key and initialization)
# openai = OpenAI(api_key="your_api_key")

# Check if session state variables are initialized
if "prompt" not in st.session_state:
    st.session_state.prompt = "Yes, I would like to buy insurance today."
if "response" not in st.session_state:
    st.session_state.response = "Great. First, can you tell me your full name?"

def run():
    st.markdown(st.session_state.prompt)
    st.toast("running")
    time.sleep(4)  # Simulating processing time
    st.session_state.response = "Cool story bro, what's your business name?"

def update_suggestions():
    placeholder = st.empty()
    suggestions = Tools.suggest_prompts(user_prompt=st.session_state.prompt, assistant_response=st.session_state.response)

    if suggestions is not None:
        container = placeholder.container()
        with container:
            for key, value in suggestions.items():
                if st.button(label=value, key=key, use_container_width=True):
                    st.session_state.prompt = value
                    run()
                    update_suggestions()

# Initial run
run()
update_suggestions()


class PromptSuggestions:
    def __init__(self, prompt, response):
        self.prompt = prompt
        self.response = response
        self.initialize()

    def initialize(self):
        self.suggestions = None
        self.prompt1 = None
        self.prompt2 = None
        self.prompt3 = None
        self.prompt4 = None
        self.placeholder = st.empty()

    def get(self):
        self.suggestions = Tools.suggest_prompts(user_prompt=self.prompt, assistant_response=self.response)
        self.prompt1 = self.suggestions['prompt1']
        self.prompt2 = self.suggestions['prompt2']
        self.prompt3 = self.suggestions['prompt3']
        self.prompt4 = self.suggestions['prompt4']
    
    def update(self):
        with self.placeholder.container():
            for key, value in self.suggestions:
                if st.button(label=value, key=key, use_container_width=True):
                    st.session_state.prompt = value
                    self.placeholder.empty()
