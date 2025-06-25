import streamlit as st
import requests
import openai
import os

# Set your endpoint URL here
ENDPOINT_URL = "https://api.vectorize.io/v1/org/dd0b48b5-0a6e-46bc-a7c7-915580d6e1f7/pipelines/aipdf4f9-e559-47a5-8650-bad7fb033cb3/retrieval"

st.set_page_config(page_title="Parent Help Line", page_icon="📞", layout="centered")

# Softer chat UI CSS
st.markdown("""
    <style>
    
    .chat-row {
        display: flex;
        align-items: flex-end;
        margin-bottom: 0.7em;
    }
    .chat-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3em;
        margin: 0 0.7em;
        flex-shrink: 0;
    }
    .chat-bubble {
        padding: 0.7em 1.2em;
        border-radius: 1.2em;
        max-width: 75%;
        word-break: break-word;
        font-size: 1.08em;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e6e6e6;
        color: #222;
    }
    .user-bubble {
        background: #e9f0fa;
        border: 1px solid #d0d7de;
        color: #222;
        border-bottom-right-radius: 0.3em;
        border-bottom-left-radius: 1.2em;
        margin-left: auto;
        margin-right: 0;
        text-align: right;
    }
    .bot-bubble {
        background: #fff;
        border: 1px solid #e6e6e6;
        color: #222;
        border-bottom-left-radius: 0.3em;
        border-bottom-right-radius: 1.2em;
        margin-right: auto;
        margin-left: 0;
        text-align: left;
    }
    .chat-header {
        text-align: center;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.1em;
        margin-top: 0.2em;
        letter-spacing: -1px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5em;
    }
    .chat-subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 1.2em;
        font-size: 1.08em;
    }
    .stTextInput > div > div > input {
        font-size: 1.1em;
        padding: 0.7em;
        border-radius: 1em;
    }
    .source-link {
        font-size: 0.98em;
        color: #1976d2;
        text-decoration: none;
        font-weight: 500;
        display: block;
        margin-top: 0.5em;
    }
    .send-row {
        display: flex;
        gap: 0.5em;
        align-items: center;
        margin-bottom: 1.5em;
        max-width: 480px;
        margin-left: auto;
        margin-right: auto;
    }
    .stButton > button {
        font-size: 1.1em;
        padding: 0.5em 1.5em;
        border-radius: 1em;
        background: #1976d2;
        color: #fff;
        border: none;
        font-weight: 600;
        margin-left: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-header">Parent Help Line</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Your AI-powered parenting help chat. Ask anything and get friendly, practical tips!</div>', unsafe_allow_html=True)

# Get the access token from Streamlit secrets
ACCESS_TOKEN = st.secrets.get("VECTORIZE_TOKEN", "")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

if not ACCESS_TOKEN:
    st.warning("Please add your VECTORIZE_TOKEN to .streamlit/secrets.toml")
if not OPENAI_API_KEY:
    st.warning("Please add your OPENAI_API_KEY to .streamlit/secrets.toml")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def summarize_with_openai(user_question, context):
    prompt = (
        f"You are a helpful parenting assistant. "
        f"Given the following information, answer the user's question in a friendly, conversational tone. "
        f"Do not use markdown. Do not mention that you are an AI. "
        f"If the information is not relevant, say you don't know.\n"
        f"\nUser question: {user_question}\n"
        f"Information: {context}\n"
        f"\nRespond conversationally and concisely."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def send_message():
    user_query = st.session_state.user_input
    if user_query and ACCESS_TOKEN and OPENAI_API_KEY:
        with st.spinner("Thinking..."):
            payload = {
                "question": user_query,
                "numResults": 5,
                "rerank": True
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": ACCESS_TOKEN
            }
            response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                docs = data.get('documents', [])
                if docs:
                    top_doc = docs[0]
                    context = top_doc.get('text', 'No tip found.')
                    source = top_doc.get('source', '')
                    source_title = top_doc.get('source_display_name', source)
                    # Summarize with OpenAI
                    summary = summarize_with_openai(user_query, context)
                    # Format: plain text summary, then reference link with title
                    if source:
                        answer = f"{summary}<br><span style='font-size:0.98em;color:#888;'>Reference:</span> <a href='{source}' class='source-link' target='_blank'>{source_title}</a>"
                    else:
                        answer = summary
                else:
                    answer = "Sorry, I couldn't find a relevant tip."
                st.session_state.chat_history.append((user_query, answer))
            else:
                st.session_state.chat_history.append((user_query, f"Error: {response.status_code} - {response.text}"))
        st.session_state.user_input = ""

# Input row with text input and send button
st.markdown('<div class="send-row">', unsafe_allow_html=True)
user_input = st.text_input('Type your message and press Enter', key='user_input', label_visibility='collapsed', placeholder='e.g. How do I help my toddler sleep through the night?')
send_clicked = st.button('Send', on_click=send_message)
st.markdown('</div>', unsafe_allow_html=True)

# All chat in a single rectangle box, with avatars and chat alignment
st.markdown('<div class="chat-outer-box">', unsafe_allow_html=True)
for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(
        f'<div class="chat-row" style="justify-content: flex-end;">'
        f'<div class="chat-bubble user-bubble">{user_msg}</div>'
        f'<div class="chat-avatar" title="You">🧑</div>'
        f'</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chat-row" style="justify-content: flex-start;">'
        f'<div class="chat-avatar" title="Parent Help Line">🤖</div>'
        f'<div class="chat-bubble bot-bubble">{bot_msg}</div>'
        f'</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) 