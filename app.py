import streamlit as st
from openai import OpenAI
from config import pagesetup as ps, sessionstate as ss
import time
from tools import Tools
import json

st.set_page_config(page_title=st.secrets.appconfig.app_name, page_icon=st.secrets.appconfig.app_icon, layout=st.secrets.appconfig.app_layout, initial_sidebar_state=st.secrets.appconfig.app_initial_sidebar)
ss.sessionstate_controller()
st.session_state.initialized = True

client = OpenAI(api_key=st.secrets.openai.api_key)
assistantid = st.secrets.openai.assistant_id
threadid = client.beta.threads.create().id




maincontainer = ps.get_userflow_setup()
with maincontainer:
    chatcontainer = st.container(height=200, border=False)
    with chatcontainer:
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

promptcontainer = st.container(border=False)
with promptcontainer:
    if prompt := st.chat_input("Enter your question or request here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chatcontainer:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            message = client.beta.threads.messages.create(thread_id=threadid, role="user", content=prompt)
            run = client.beta.threads.runs.create(thread_id=threadid, assistant_id=assistantid, additional_instructions="Do NOT use any tools of type functions for this run.")

            status = None
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
                    for threadmessage in threadmessages:
                        if threadmessage.role == "assistant" and threadmessage.run_id == run.id:
                            st.session_state.messages.append({"role": "assistant", "content": threadmessage.content[0].text.value})
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

