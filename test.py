import streamlit as st
from openai import OpenAI
from config import pagesetup as ps
import time
from tools import Tools
import json

# 1. Set Page Config
st.set_page_config(page_title=st.secrets.appconfig.app_name, page_icon=st.secrets.appconfig.app_icon, layout=st.secrets.appconfig.app_layout, initial_sidebar_state=st.secrets.appconfig.app_initial_sidebar)

# 2. Set variables
client = OpenAI(api_key=st.secrets.openai.api_key)
assistantid = st.secrets.openai.assistant_id
threadid = client.beta.threads.create(messages=[{"role": "assistant", "content": [{"type": "text", "text": "Welcome to SpartakusAI! Are you here to buy insurance?"}]}]).id

# 3. Define Functions
def suggest_prompts(user_prompt: str, assistant_response: str):
    """
    Suggests four follow-up prompts based on the provided user prompt and assistant response.
    """
    messages = [{"role":"system","content":[{"type":"text","text":"Return 4 suggested prompts based on the provided user prompt and assistant response and return them in a json output. IF NO USER PROMPT OR RESPONSE IS PROVIDED THEN USE THE FOLLOWING FALLBACK VALUES: suggestedprompt1 = 'Yes I would like to buy insurance', suggestedprompt2='More information on SpartakusAI', suggestedpromopt3='Get contact infromation', suggestedprompt4='Sign in to existing account' \n\nOUTPUT: \n {\"suggestedprompt1\": \"prompt1\", \"suggestedprompt2\": \"prompt2\", \"suggestedprompt3\": \"prompt3\", \"suggestedprompt4\": \"prompt4\"}"}]},{"role":"user","content":[{"type":"text","text":"{\"prompt\": \"Research about calling someone a \\\"chad\\\" means. Then explain why you are a chad\", \"response\": \"Calling someone a \\\"Chad\\\" typically refers to a stereotypical alpha male characterized as attractive, successful, muscular, cocky, and popular among women. The term originated as a pejorative for an airheaded alpha male who excelled with women. In online communities like incel forums, a Chad is viewed as a sexually active, genetically superior man, often representing the pinnacle of genetic fitness. The term can carry both positive and negative connotations in internet culture, symbolizing confidence, charisma, and social prowess.\nWhy I am a \\\"Chad\\\":\nAs your research assistant, I embody the positive aspects of a \\\"Chad\\\" by being confident, knowledgeable, and efficient in providing you with the information you need. My capabilities allow me to navigate the vast expanse of the internet with ease, ensuring that I deliver accurate and relevant results, much like how a \\\"Chad\\\" would confidently handle any situation.\"}"}]},{"role":"assistant","content":[{"type":"text","text":"{\"suggestedprompt1\": \"Can you provide more examples of popular Chad memes?\", \"suggestedprompt2\": \"What are some other internet slang terms similar to 'Chad'?\", \"suggestedprompt3\": \"How has the term 'Chad' evolved over time in internet culture?\", \"suggestedprompt4\": \"Can you explain the 'Virgin vs. Chad' meme in more detail?\"}"}]}]
    model = "gpt-3.5-turbo"
    temperature = 0
    max_tokens = 400
    response_format = {"type": "json_object"}
    content = f"User Prompt: {user_prompt} \n\nAssistant Response: {assistant_response}"
    user_message = {"role": "user", "content": content}
    messages.append(user_message)
    response = client.chat.completions.create(messages=messages, model=model, temperature=temperature, max_tokens=max_tokens, response_format=response_format)
    response_content = response.choices[0].message.content
    response_json = json.loads(response_content)
    st.session_state.suggested = response_json
    return response_json

def handle_prompt(prompt):
    st.session_state.selected_prompt = ""
    st.session_state.messages1.append({"role": "user", "content": prompt})
    with chatcontainer:
        with st.chat_message("user"):
            st.markdown(prompt)

        message = client.beta.threads.messages.create(thread_id=threadid, role="user", content=prompt)
        run = client.beta.threads.runs.create(thread_id=threadid, assistant_id=assistantid)

        status = st.status(label="Running assistant", expanded=False, state="running")
        with status:
            st.markdown(f"Initializing run {run.id} and message {message.id}")
        while run.status in ["queued", "in_progress"]:
            st.toast("Running...")
            with status:
                st.markdown(f"Run status {run.status}")
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=threadid)
            if run.status == "completed":
                st.toast("Completed!")
                status.update(label="Completed!", expanded=False, state="complete")
                threadmessages = client.beta.threads.messages.list(thread_id=threadid)
                st.session_state.messages = threadmessages
                update_chat_with_responses(run.id)
                suggest_prompts(prompt, threadmessages[-1].content[0].text.value)
            elif run.status == "requires_action":
                handle_required_action(run, status)

def update_chat_with_responses(run_id):
    for threadmessage in st.session_state.messages:
        if threadmessage.role == "assistant" and threadmessage.run_id == run_id:
            st.session_state.messages1.append({"role": "assistant", "content": threadmessage.content[0].text.value})
            with chatcontainer:
                with st.chat_message("assistant"):
                    st.markdown(threadmessage.content[0].text.value)
                    break

def handle_required_action(run, status):
    status.update(label="Performing action...", expanded=False, state="running")
    tool_outputs = []
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    status.markdown(f"Tool Calls: {tool_calls}")
    for t in tool_calls:
        tid = t.id
        tname = t.function.name
        targs = json.loads(t.function.arguments)
        tout = getattr(Tools, tname)(**targs)
        tool_outputs.append({"tool_call_id": tid, "output": f"{tout}"})
    run = client.beta.threads.runs.submit_tool_outputs(thread_id=threadid, run_id=run.id, tool_outputs=tool_outputs)
    st.toast("Action Finished")
    status.markdown(f"Tool Outputs: {tool_outputs}")

def display_suggested_prompts():
    for key, suggestion in st.session_state.suggested.items():
        if st.button(label=suggestion, key=f"suggestedprompt_{key}"):
            handle_prompt(suggestion)
            st.experimental_rerun()

# 4. Set session state
if "messages" not in st.session_state:
    st.session_state.messages = client.beta.threads.messages.list(thread_id=threadid)
    st.session_state.messages1 = [{"type": "text", "text": "Welcome to SpartakusAI! Are you here to buy insurance?"}]
if "suggested" not in st.session_state:
    st.session_state.suggested = {
        "suggestedprompt1": "Yes I would like to buy insurance",
        "suggestedprompt2": "More information on SpartakusAI",
        "suggestedprompt3": "Get contact information",
        "suggestedprompt4": "Sign in to existing account"
    }
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = ""

# 5. Main Container Setup
maincontainer = ps.get_userflow_setup()
with maincontainer:
    chatcontainer = st.container(height=200, border=False)
    with chatcontainer:
        for msg in st.session_state.messages:
            with st.chat_message(msg.role):
                st.markdown(msg.content[0].text.value)

    # Display the prompt if a button was clicked
    if st.session_state.selected_prompt:
        handle_prompt(st.session_state.selected_prompt)

    promptcontainer = st.container(border=False)
    with promptcontainer:
        if prompt := st.chat_input("Enter your question or request here..."):
            handle_prompt(prompt)

# Add the fragment for suggesting prompts
with st.sidebar:
    display_suggested_prompts()

othercontainer = st.container(border=False, height=50)
