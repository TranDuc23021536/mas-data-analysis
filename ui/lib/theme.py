import streamlit as st

PRIMARY_COLOR = "#2563EB"


def apply_theme():
    st.markdown(
        f"""
        <style>
        .stButton>button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )