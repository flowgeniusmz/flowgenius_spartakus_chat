import streamlit as st
from openai import OpenAI as openai_client
from tavily import TavilyClient as tavily_client
from supabase import create_client as supabase_client
from googlemaps import places, geocoding, addressvalidation, Client as google_client
from googlesearch import search
from yelpapi import YelpAPI as yelp_client
import time
import json
import datetime
from typing import Literal
import pandas as pd
import asyncio



##### SET CLIENTS
oaiClient = openai_client(api_key=st.secrets.openai.api_key)
supaClient = supabase_client(supabase_key=st.secrets.supabase.api_key_admin, supabase_url=st.secrets.supabase.url)
yelpClient = yelp_client(api_key=st.secrets.yelp.api_key)
googClient = google_client(key=st.secrets.google.maps_api_key)
tavClient = tavily_client(api_key=st.secrets.tavily.api_key)

##### SET VARIABLES
assistantid = st.secrets.openai.assistant_id
threadid = st.secrets.openai.thread_id





###### CLASSES
#__________________________________________________________________________________________
# 1. Tools
class Tools:
    @staticmethod
    def execute_all_searches(query: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(AsyncTools.execute_all_tasks(query))
        responses_content = f"All Search Results: {responses}"
        return responses_content
    
    @staticmethod
    def suggest_prompts(user_prompt: str, assistant_response: str):
        """
        Suggests four follow-up prompts based on the provided user prompt and assistant response.

        Args:
            user_prompt (str): The initial prompt provided by the user.
            assistant_response (str): The response provided by the assistant.

        Returns:
            dict: A dictionary containing four suggested prompts.
        """
        messages=[{"role": "system", "content": [{"type": "text", "text": "-You are a commercial insurance processing expert. \n-Your job is to recommend or suggest prompts to the user that they can use next. \n-The user is providing information related to themselves, their business and ultimately insurance accord forms.\n-You will ensure your prompt suggestions take this context into account. \n-You will never ask about personal related insurance or assets - this is commercial insurance.\n-You will be given the most recent user prompt and associated assistant response. \n-You will generate EXACTLY 4 prompt suggestions and return them in a json object using the sample output provided. \n-You will ensure the json object uses the exact same keys as listed below. \n-You will ensure your prompt suggestions are 30 characters are less. \n-YOU WILL BE SUPER QUICK AND EFFICIENT.\n-YOU ARE PROVIDING PROMPTS FROM THE PERSPECTIVE OF THE USER - NOT THE ASSISTANT ASKING THE QUESTIONS YOU PIECE OF SHIT\n\n### JSON OUTPUT TEMPLATE ###\n{\"prompt1\": {prompt1_value}, \"prompt2\": {prompt2_value}, \"prompt3\": {prompt3_value}, \"prompt4\": {prompt4_value}}"}]}, {"role": "user", "content": [{"type": "text", "text": "User Prompt: Yes I would like to buy insurance today.\nAssistant Response: Great - what kind of insurance are you looking to buy?"}]}, {"role": "assistant", "content": [{"type": "text", "text": "{ \"prompt1\": \"I'm looking to buy general liability insurance for my small business.\", \"prompt2\": \"I need commercial property insurance for my new office space.\", \"prompt3\": \"I'm interested in getting workers' compensation insurance for my employees.\", \"prompt4\": \"I want to explore options for professional liability insurance for my consulting firm.\" }"}]}, {"role": "user", "content": [{"type": "text", "text": "User Prompt: I want to explore options for professional liability insurance for my consulting firm.\nAssistant Response: Thank you for your interest in professional liability insurance for your consulting firm. Professional liability insurance, also known as errors and omissions (E&O) insurance, is designed to protect your business against claims of negligence, errors, or omissions in the services you provide to your clients.\nTo get started, I'll need to gather some information about your business. Could you please provide the following details:\nThe full name of your consulting firm.\nThe primary address of your business.\nA brief description of the consulting services you offer.\nThe number of employees in your firm.\nYour annual revenue.\nOnce I have this information, I can provide you with a more accurate quote and discuss the coverage options available to you. If you have any specific questions about professional liability insurance, feel free to ask!\"\nThis response ensures that the user feels informed and supported while gathering the necessary information to proceed with the insurance process."}]}, {"role": "assistant", "content": [{"type": "text", "text": "{ \"prompt1\": \"Can you explain what professional liability insurance covers?\", \"prompt2\": \"What information do you need from me to get a quote for professional liability insurance?\", \"prompt3\": \"Are there any specific exclusions in professional liability insurance policies?\", \"prompt4\": \"How does professional liability insurance differ from general liability insurance?\" }"}]}, {"role": "user", "content": [{"type": "text", "text": "User Prompt: {user_prompt} \n\nAssistant Response: {assistant_response}"}]}]
        model = "gpt-3.5-turbo"
        temperature = 0
        max_tokens = 400
        response_format = {"type": "json_object"}
        content = f"User Prompt: {user_prompt} \n\nAssistant Response: {assistant_response}"
        user_message = {"role": "user", "content": content}
        messages.append(user_message)
        response = oaiClient.chat.completions.create(messages=messages, model=model, temperature=temperature, max_tokens=max_tokens, response_format=response_format)
        response_content = response.choices[0].message.content
        response_json = json.loads(response_content)
        print(response_json)
        st.session_state.suggestions = response_json
        st.session_state.suggestion1 = response_json['prompt1']
        st.session_state.suggestion2 = response_json['prompt2']
        st.session_state.suggestion3 = response_json['prompt3']
        st.session_state.suggestion4 = response_json['prompt4']
        return response_json
    
    @staticmethod
    def internet_search(query: str):
        """
        Performs an internet search using the provided query and returns a list of search results.

        Args:
            query (str): The search query.

        Returns:
            list: A list of URLs corresponding to the search results.
        """
        response = search(term = query, advanced=True)
        responselist = list(response)
        return responselist
    
    @staticmethod
    def internet_research(query: str):
        """
        Performs advanced internet research using the provided query and returns the results.

        Args:
            query (str): The research query.

        Returns:
            dict: The research results, including answers and raw content.
        """
        response = tavClient.search(query=query, search_depth="advanced", max_results=7, include_answer=True, include_raw_content=True)
        return response
    
    @staticmethod
    def google_places_search(query: str):
        """
        Searches for business information using Google Places to gather details on location, ratings, and more.
        
        Parameters:
            query (str): The search query describing the business.
        
        Returns:
            dict: The search results with detailed information about the business.
        """
        response = places.places(client=googClient, query=query, region="US")
        return response
    
    @staticmethod
    def google_address_validation(address_lines: list):
        """
        Validates business addresses using Google Address Validation to ensure accuracy for insurance documentation.
        
        Parameters:
            address_lines (list): The address lines to be validated.
        
        Returns:
            dict: The validation results including any corrections or standardizations.
        """
        response = addressvalidation.addressvalidation(client=googClient, addressLines=address_lines, regionCode="US", enableUspsCass=True)
        return response
    
    @staticmethod
    def google_geocode(address_lines: list):
        """
        Geocodes business addresses using Google Geocoding to obtain latitude and longitude for location verification.
        
        Parameters:
            address_lines (list): The address lines to be geocoded.
        
        Returns:
            dict: The geocoding results with latitude and longitude coordinates.
        """
        response = geocoding.geocode(client=googClient, address=address_lines, region="US")
        return response
    
    

#__________________________________________________________________________________________
# 2. Tool Schemas
class ToolSchemas:
    suggest_prompts = {
        "name": "suggest_prompts",
        "description": "Suggests four follow-up prompts based on the provided user prompt and assistant response.",
        "parameters": {
            "type": "object",
            "properties": {
            "user_prompt": {
                "type": "string",
                "description": "The initial prompt provided by the user."
            },
            "assistant_response": {
                "type": "string",
                "description": "The response provided by the assistant."
            }
            },
            "required": ["user_prompt", "assistant_response"]
        }
        }


    internet_search = {
        "name": "internet_search",
        "description": "Performs an internet search using the provided query and returns a list of search results.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            }
            },
            "required": ["query"]
        }
        }

    internet_research = {
        "name": "internet_research",
        "description": "Performs advanced internet research using the provided query and returns the results.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The research query."
            }
            },
            "required": ["query"]
        }
        }

    google_places_search = {
        "name": "google_places_search",
        "description": "Searches for business information using Google Places to gather details on location, ratings, and more.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The search query describing the business."
            }
            },
            "required": ["query"]
        }
        }

    google_address_validation = {
        "name": "google_address_validation",
        "description": "Validates business addresses using Google Address Validation to ensure accuracy for insurance documentation.",
        "parameters": {
            "type": "object",
            "properties": {
            "address_lines": {
                "type": "array",
                "items": {
                "type": "string"
                },
                "description": "The address lines to be validated."
            }
            },
            "required": ["address_lines"]
        }
        }

    google_geocode = {
        "name": "google_geocode",
        "description": "Geocodes business addresses using Google Geocoding to obtain latitude and longitude for location verification.",
        "parameters": {
            "type": "object",
            "properties": {
            "address_lines": {
                "type": "array",
                "items": {
                "type": "string"
                },
                "description": "The address lines to be geocoded."
            }
            },
            "required": ["address_lines"]
        }
        }

    

    execute_all_searches = {
        "name": "execute_all_searches",
        "description": "Executes internet_search, internet_research, google_places_search asynchronously and returns all the responses.",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            }
            },
            "required": ["query"]
        }
        }

#__________________________________________________________________________________________
# 3. Async Tools
class AsyncTools:
    @staticmethod
    async def internet_search(query: str):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: list(search(term=query, advanced=True)))
        return response
    
    @staticmethod
    async def internet_research(query: str):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: tavClient.search(query=query, search_depth="advanced", max_results=7, include_answer=True, include_raw_content=True))
        return response

    @staticmethod
    async def google_places_search(query: str):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: googClient.places(query=query, region="US"))
        return response
    
    
    @staticmethod
    async def execute_all_tasks(query: str):
        tasks = [
            AsyncTools.internet_search(query),
            AsyncTools.internet_research(query),
            AsyncTools.google_places_search(query)
        ]

        responses = await asyncio.gather(*tasks)
        return {
            "internet_search": responses[0],
            "internet_research": responses[1],
            "google_places_search": responses[2]
        }

