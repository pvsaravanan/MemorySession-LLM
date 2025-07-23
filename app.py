from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
LOCAL_MODEL_NAME = os.environ.get("LOCAL_MODEL_NAME")
REMOTE_MODEL_NAME = os.environ.get("REMOTE_MODEL_NAME")
LOCAL_BASE_URL = os.environ.get("LOCAL_BASE_URL")
REMOTE_BASE_URL = os.environ.get("REMOTE_BASE_URL")

# Initialize LLMs
cloud_llm = None
if REMOTE_MODEL_NAME:
    cloud_llm = ChatOpenAI(
        model=REMOTE_MODEL_NAME,
        api_key=OPENROUTER_API_KEY,
        base_url=REMOTE_BASE_URL
    )

local_llm = None
if LOCAL_MODEL_NAME:
    local_llm = ChatOllama(
        model=LOCAL_MODEL_NAME,
        base_url=LOCAL_BASE_URL
    )

# App title and UI tweaks
st.set_page_config(page_title="💬 Talk to Me", layout="centered")
st.markdown(
    """
    <style>
    .stChatMessage {
        # padding: 10px;
        # margin: 10px 0;
        # border-radius: 12px;
        # line-height: 1.5;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 16px;
        line-height: 1.5;
    }
    .user-bubble {
        # background-color: #DCF8C6;
        text-align: right;
        background-color: #d4f8c4;
        color: #1e1e1e;
        align-self: flex-end;
        font-weight: 600;
    }
    .assistant-bubble {
        # background-color: #F1F0F0;
        background-color: #d4f8c4;
        color: #1e1e1e;
        # color: #e0e0e0;      /* Brighter than light gray */
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Talk to Me")

# Toggle model
think_harder = st.toggle("🤖 Think harder (use cloud model)", value=False)

# Message memory
st.session_state.setdefault("messages", [])

# Display history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        bubble_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f"<div class='stChatMessage {bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# Input prompt
prompt = st.chat_input("Type your message...")

# If user submits a message
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state["messages"]])
            llm = cloud_llm if think_harder else local_llm

            if llm:
                response = llm.invoke(context)
                # Typing animation effect
                response_text = response.content
                assistant_msg = ""
                placeholder = st.empty()
                for char in response_text:
                    assistant_msg += char
                    placeholder.markdown(f"<div class='stChatMessage assistant-bubble'>{assistant_msg}</div>", unsafe_allow_html=True)
                    time.sleep(0.015)
                st.session_state["messages"].append({"role": "assistant", "content": response_text})
            else:
                st.warning("LLM not initialized.")