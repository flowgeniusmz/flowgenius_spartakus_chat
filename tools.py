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
threadid = st.session_state.threadid





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
        messages = [{"role":"system","content":[{"type":"text","text":"Return 4 suggested prompts based on the provided user prompt and assistant response and return them in a json output. IF NO USER PROMPT OR RESPONSE IS PROVIDED THEN USE THE FOLLOWING FALLBACK VALUES: suggestedprompt1 = 'Yes I would like to buy insurance', suggestedprompt2='More information on SpartakusAI', suggestedpromopt3='Get contact infromation', suggestedprompt4='Sign in to existing account' \n\nOUTPUT: \n {\"suggestedprompt1\": \"prompt1\", \"suggestedprompt2\": \"prompt2\", \"suggestedprompt3\": \"prompt3\", \"suggestedprompt4\": \"prompt4\"}"}]},{"role":"user","content":[{"type":"text","text":"{\"prompt\": \"Research about calling someone a \\\"chad\\\" means. Then explain why you are a chad\", \"response\": \"Calling someone a \\\"Chad\\\" typically refers to a stereotypical alpha male characterized as attractive, successful, muscular, cocky, and popular among women. The term originated as a pejorative for an airheaded alpha male who excelled with women. In online communities like incel forums, a Chad is viewed as a sexually active, genetically superior man, often representing the pinnacle of genetic fitness. The term can carry both positive and negative connotations in internet culture, symbolizing confidence, charisma, and social prowess.\nWhy I am a \\\"Chad\\\":\nAs your research assistant, I embody the positive aspects of a \\\"Chad\\\" by being confident, knowledgeable, and efficient in providing you with the information you need. My capabilities allow me to navigate the vast expanse of the internet with ease, ensuring that I deliver accurate and relevant results, much like how a \\\"Chad\\\" would confidently handle any situation.\"}"}]},{"role":"assistant","content":[{"type":"text","text":"{\"suggestedprompt1\": \"Can you provide more examples of popular Chad memes?\", \"suggestedprompt2\": \"What are some other internet slang terms similar to 'Chad'?\", \"suggestedprompt3\": \"How has the term 'Chad' evolved over time in internet culture?\", \"suggestedprompt4\": \"Can you explain the 'Virgin vs. Chad' meme in more detail?\"}"}]}]
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
        st.session_state.suggestion1 = response_json['suggestedprompt1']
        st.session_state.suggestion2 = response_json['suggestedprompt2']
        st.session_state.suggestion3 = response_json['suggestedprompt3']
        st.session_state.suggestion4 = response_json['suggestedprompt4']
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

