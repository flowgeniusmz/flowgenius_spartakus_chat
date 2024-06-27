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
    st.session_state.response2 = """Certainly! Here is the assistant response for the prompt "What information do you need from me to get a quote for professional liability insurance?" --- "To provide you with an accurate quote for professional liability insurance, I'll need the following information about your consulting firm: 1. The full name of your consulting firm. 2. The primary address of your business. 3. A brief description of the consulting services you offer. 4. The number of employees in your firm. 5. Your annual revenue. 6. Any previous claims or losses related to professional liability. 7. The desired coverage limits and any specific requirements you may have. Once I have this information, I can proceed with generating a quote and discussing the coverage options available to you. If you have any questions or need further clarification, please let me know!" --- This response ensures that the user understands the necessary information required to proceed with the quote and feels supported throughout the process."""




class PromptSuggestions:
    def __init__(self, prompt, response):
        self.prompt = prompt
        self.response = response
        self.initialize()
        self.get()
        self.update()

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
            for key, value in self.suggestions.items():
                if st.button(label=value, key=key, use_container_width=True):
                    st.session_state.prompt = value
                    self.placeholder.empty()


PromptSuggestions(prompt=st.session_state.prompt, response=st.session_state.response)
time.sleep(4)
PromptSuggestions(prompt=st.session_state.prompt, response=st.session_state.response2)