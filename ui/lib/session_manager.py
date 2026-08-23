import streamlit as st


def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None


def add_turn(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})


def clear_session():
    st.session_state.chat_history = []
    st.session_state.session_id = None