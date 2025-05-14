import streamlit as st
from agents.agent import run
import asyncio

# Initialize session state variables
if 'response' not in st.session_state:
    st.session_state.response = {}

if 'trending' not in st.session_state:
    st.session_state.trending = []

if 'lattest' not in st.session_state:
    st.session_state.lattest = []

if 'get_trending' not in st.session_state:
    st.session_state.get_trending = []

if 'get_lattest' not in st.session_state:
    st.session_state.get_lattest = []

if 'history' not in st.session_state:
    st.session_state.history = {}

if 'messages' not in st.session_state:
    st.session_state.messages = []

def chat(prompt):
    return run(prompt)

st.set_page_config(page_title="LLM Papers with Code", page_icon=":books:", layout='wide')
st.title("Agentic queries for papers with Code")

st.markdown('''# How to use the agentic paper scraper
1. Enter your prompt asking to add the papers wheter they are trending or lattest to the database.
2. The agent will get if you want to add trending or lattest papers to the database.
3. Click the submit prompt button.
4. The streamlit will show all the papers that were added.
5. After you've added the papers to the choosen database you can query the topic and how many papers you want to get.
6. The agent will query the database and return the papers.
'''
)

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("What is up?"):
    with st.chat_message('user'):
        st.markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('assistant'):
        response_stream = chat(prompt)
        response = st.write_stream(response_stream)
        st.session_state.messages.append({'role': 'assistant', 'content': response})

with st.sidebar:
    st.markdown('## Find specifics of the chat')
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
