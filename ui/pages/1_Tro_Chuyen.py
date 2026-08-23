import streamlit as st
from lib.theme import apply_theme
from lib.session_manager import init_session, add_turn
from lib.api_client import analyze

st.set_page_config(page_title="Tro Chuyen", layout="centered")
apply_theme()
init_session()

st.title("Tro chuyen voi he thong")

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

question = st.chat_input("Nhap cau hoi ve du lieu kinh doanh...")

if question:
    add_turn("user", question)
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Dang phan tich..."):
            try:
                result = analyze(question, st.session_state.session_id)
                st.session_state.session_id = result.get("session_id")
            except Exception as e:
                st.error(f"Co loi xay ra: {e}")
                result = None

        if result:
            st.write(result["final_answer"])

            if not result.get("is_valid", True):
                st.warning("Critic Agent phat hien cau tra loi co the chua chinh xac hoan toan, hay kiem tra lai.")

            if result.get("chart_type", "none") != "none" and result.get("chart_data"):
                import pandas as pd
                df = pd.DataFrame(result["chart_data"])
                if result["chart_type"] == "bar":
                    st.bar_chart(df.set_index(df.columns[0]))
                elif result["chart_type"] == "line":
                    st.line_chart(df.set_index(df.columns[0]))
                else:
                    st.dataframe(df)

            if result.get("forecast_result"):
                st.subheader("Du bao")
                st.dataframe(pd.DataFrame(result["forecast_result"]))

            if result.get("anomaly_result"):
                st.subheader("Bat thuong phat hien duoc")
                st.dataframe(pd.DataFrame(result["anomaly_result"]))

            add_turn("assistant", result["final_answer"])

if st.button("Xoa hoi thoai"):
    from lib.session_manager import clear_session
    clear_session()
    st.rerun()