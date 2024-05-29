import streamlit as st

def initialize_session_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user = None
        st.session_state.userrole = None
        st.session_state.username = None
        st.session_state.password = None
        st.session_state.email = None
        st.session_state.firstname = None
        st.session_state.lastname = None
        st.session_state.fullname = None
        st.session_state.businessid = None
        st.session_state.businessname = None
        st.session_state.businessaddress = None
        st.session_state.vectorstore = None
        st.session_state.thread = None
        st.session_state.threadid = None
        st.session_state.vectorstoreid = None
        st.session_state.createddate = None
        st.session_state.request_headers = {'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9','Accept-Encoding': 'gzip, deflate, br'}
        st.session_state.authenticated = False
        st.session_state.userflow_complete = False
        st.session_state.userflow_authenticated = False
        st.session_state.userflow_submitted = False
        st.session_state.userdata = None
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to SpartakusAI! I am Sparty - how may I help you today?"}]
        st.session_state.threadmessages = None
        st.session_state.f36 = False
        st.session_state.f125 = False
        st.session_state.f126 = False
        st.session_state.f127 = False
        st.session_state.f130 = False
        st.session_state.f133 = False
        st.session_state.f137 = False
        st.session_state.f140 = False
        
        
def sessionstate_controller():
    if "initialized" not in st.session_state:
        initialize_session_state()
    elif not st.session_state.initialized:
        initialize_session_state()
