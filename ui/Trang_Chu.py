import streamlit as st
from lib.theme import apply_theme
from lib.session_manager import init_session, add_turn
from lib.api_client import analyze, upload_file, list_uploaded_tables

st.set_page_config(page_title="MAS Data Analysis", layout="centered")
apply_theme()
init_session()

st.markdown(
    """
    <div class="mas-hero">
        <h1>Multi-Agent Data Analysis System</h1>
        <p>He thong AI da tac tu ho tro phan tich du lieu kinh doanh bang ngon ngu tu nhien.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Tai du lieu rieng len de phan tich (CSV/Excel)"):
    uploaded = st.file_uploader("Chon file", type=["csv", "xlsx"])
    if uploaded is not None:
        if st.button("Tai len"):
            with st.spinner("Dang xu ly file..."):
                try:
                    result = upload_file(uploaded.read(), uploaded.name)
                    st.success(f"Da tao bang '{result['table_name']}' voi {result['rows_loaded']} dong, cot: {', '.join(result['columns'])}")
                except Exception as e:
                    st.error(f"Loi khi tai file: {e}")

    try:
        tables = list_uploaded_tables()
        if tables:
            st.caption(f"Cac bang da tai len: {', '.join(tables)}")
    except Exception:
        pass

st.subheader("Lich su hoi thoai")

if not st.session_state.chat_history:
    st.caption("Chua co hoi thoai nao. Dat cau hoi ben duoi de bat dau.")

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

if st.session_state.chat_history:
    if st.button("Xoa hoi thoai"):
        from lib.session_manager import clear_session
        clear_session()
        st.rerun()