import streamlit as st
from agents.agent import run
import asyncio

class WebSocketManager:
    def __init__(self, url: str = "ws://llm-service:8765"):
        self.url = url
        self.connection = None

    async def connect(self):
        try:
            self.connection = await websockets.connect(self.url)
            return True
        except Exception as e:
            st.error(f"WebSocket connection error: {e}")
            return False

    async def send_message(self, message: str) -> Optional[Dict[str, Any]]:
        if not self.connection:
            if not await self.connect():
                return None
        
        try:
            await self.connection.send(message)
            response = await self.connection.recv()
            return json.loads(response)
        except Exception as e:
            st.error(f"Error sending/receiving message: {e}")
            return None

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None

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

async def process_message(prompt: str) -> str:
    """Send message to WebSocket and get response"""
    if not st.session_state.ws_manager.connection:
        connected = await st.session_state.ws_manager.connect()
        if not connected:
            return "Error: Could not connect to the LLM service"

    response = await st.session_state.ws_manager.send_message(prompt)
    if response and 'response' in response:
        return response['response']
    elif response and 'error' in response:
        return f"Error: {response['error']}"
    else:
        return "Error: No response from the server"

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

    async def process_and_display():
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                response = await process_message(prompt)
                st.markdown(response)
                st.session_state.messages.append({'role': 'assistant', 'content': response})
                
    asyncio.run(process_and_display())


with st.sidebar:
    st.markdown('## Find specifics of the chat')
    
    if st.button("Clear Chat"):
        st.session_state.messages = []

import atexit

def cleanup():
    if 'ws_manager' in st.session_state:
        asyncio.run(st.session_state.ws_manager.close())

atexit.register(cleanup)
