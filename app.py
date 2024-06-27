import streamlit as st
from openai import OpenAI
from config import pagesetup as ps
import time
from tools import Tools
import json

# 1. Set Page Config
#st.set_page_config(page_title=st.secrets.appconfig.app_name, page_icon=st.secrets.appconfig.app_icon, layout=st.secrets.appconfig.app_layout, initial_sidebar_state=st.secrets.appconfig.app_initial_sidebar)


# 2. Set variables
client = OpenAI(api_key=st.secrets.openai.api_key)
assistantid = st.secrets.openai.assistant_id
threadid = client.beta.threads.create(messages=[{"role": "assistant", "content": [{"type": "text", "text": "Welcome to SpartakusAI! Are you here to buy insurance?"}]}]).id


    

# 2. Set session state
if "messages" not in st.session_state:
    st.session_state.messages = client.beta.threads.messages.list(thread_id=threadid)
    st.session_state.messages1 = [{"type": "text", "text": "Welcome to SpartakusAI! Are you here to buy insurance?"}]

if "suggested" not in st.session_state:
    st.session_state.suggested = {"suggestedprompt1": "Yes I would like to buy insurance", "suggestedprompt2": "Tell me about SpartakusAI", "suggestedprompt3": "Need contact information", "suggestedprompt4": "Why use SpartakusAI?"}
    st.session_state.suggestedprompt1 = st.session_state.suggested['suggestedprompt1']
    st.session_state.suggestedprompt2 = st.session_state.suggested['suggestedprompt2']
    st.session_state.suggestedprompt3 = st.session_state.suggested['suggestedprompt3']
    st.session_state.suggestedprompt4 = st.session_state.suggested['suggestedprompt4']



maincontainer = ps.get_userflow_setup()
with maincontainer:
    chatcontainer = st.container(height=200, border=False)
    with chatcontainer:
        for msg in st.session_state.messages:
            with st.chat_message(msg.role):
                st.markdown(msg.content[0].text.value)

promptcontainer = st.container(border=False)
with promptcontainer:
    if prompt := st.chat_input("Enter your question or request here..."):
        st.session_state.messages1.append({"role": "user", "content": prompt})
        print(st.session_state.messages)
        with chatcontainer:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            message = client.beta.threads.messages.create(thread_id=threadid, role="user", content=prompt)
            run = client.beta.threads.runs.create(thread_id=threadid, assistant_id=assistantid)

            
            status = st.status(label="Running assistant", expanded=False, state="running")
            with status:
                st.markdown(f"Initializing run {run.id} and message {message.id}")
            while run.status == "queued" or run.status == "in_progress":
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
                    for threadmessage in threadmessages:
                        if threadmessage.role == "assistant" and threadmessage.run_id == run.id:
                            st.session_state.messages1.append({"role": "assistant", "content": threadmessage.content[0].text.value})
                            with chatcontainer:
                                with st.chat_message("assistant"):
                                    st.markdown(threadmessage.content[0].text.value)
                                    break
                elif run.status == "requires_action":
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

    
othercontainer = st.container(border=False, height=50)

