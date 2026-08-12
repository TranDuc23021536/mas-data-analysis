import streamlit as st
import requests

API_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="MAS Data Analysis", layout="centered")
st.title("Multi-Agent Data Analysis")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

question = st.chat_input("Nhập câu hỏi về dữ liệu kinh doanh...")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích..."):
            response = requests.post(API_URL, json={
                "question": question,
                "chat_history": st.session_state.chat_history[:-1],
            })

        if response.status_code == 200:
            data = response.json()
            st.write(data["final_answer"])

            if data["chart_type"] != "none" and data["chart_data"]:
                import pandas as pd
                df = pd.DataFrame(data["chart_data"])
                if data["chart_type"] == "bar":
                    st.bar_chart(df.set_index(df.columns[0]))
                elif data["chart_type"] == "line":
                    st.line_chart(df.set_index(df.columns[0]))
                else:
                    st.dataframe(df)

            st.session_state.chat_history.append({"role": "assistant", "content": data["final_answer"]})
        else:
            st.error("Có lỗi xảy ra, vui lòng thử lại.")