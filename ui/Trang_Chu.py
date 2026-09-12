import streamlit as st
from lib.theme import apply_theme
from lib.session_manager import init_session, add_turn
from lib.api_client import analyze_stream, upload_file, list_uploaded_tables

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

_AVATARS = {"user": "🧑", "assistant": "🤖"}

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"], avatar=_AVATARS.get(turn["role"])):
        st.write(turn["content"])

question = st.chat_input("Nhap cau hoi ve du lieu kinh doanh...")

if question:
    add_turn("user", question)
    with st.chat_message("user", avatar=_AVATARS["user"]):
        st.write(question)

    with st.chat_message("assistant", avatar=_AVATARS["assistant"]):
        progress_placeholder = st.empty()
        result = None

        try:
            for event_type, data in analyze_stream(question, st.session_state.session_id):
                if event_type == "progress":
                    progress_placeholder.info(data.get("label", ""))
                elif event_type == "final":
                    result = data
                    st.session_state.session_id = result.get("session_id")
                elif event_type == "error":
                    st.error(f"Co loi xay ra: {data.get('detail', '')}")
        except Exception as e:
            st.error(f"Co loi xay ra: {e}")

        progress_placeholder.empty()

        if result:
            st.write(result["final_answer"])

            if not result.get("is_valid", True):
                st.warning("Critic Agent phat hien cau tra loi co the chua chinh xac hoan toan, hay kiem tra lai.")

            if result.get("chart_type", "none") != "none" and result.get("chart_data"):
                import pandas as pd
                df = pd.DataFrame(result["chart_data"])

                label_col = df.columns[0]
                value_cols = [c for c in df.columns if c != label_col]
                for c in value_cols:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

                df = df.set_index(label_col)

                if result["chart_type"] == "bar":
                    st.bar_chart(df, height=400, use_container_width=True)
                elif result["chart_type"] == "line":
                    st.line_chart(df, height=400, use_container_width=True)
                elif result["chart_type"] == "pie":
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    df[value_cols[0]].plot.pie(ax=ax, autopct="%1.1f%%", ylabel="")
                    st.pyplot(fig)
                else:
                    st.dataframe(df, use_container_width=True)

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