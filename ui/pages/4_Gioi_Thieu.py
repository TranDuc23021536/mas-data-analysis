import streamlit as st
from lib.theme import apply_theme

st.set_page_config(page_title="Gioi Thieu", layout="centered")
apply_theme()

st.title("Gioi thieu he thong")

st.write("""
Multi-Agent Data Analysis System la he thong AI da tac tu ho tro phan tich du lieu kinh doanh
bang ngon ngu tu nhien, xay dung bang LangGraph va Groq API.
""")

st.subheader("Kien truc")
st.write("""
- Planner Agent: phan tich cau hoi, xac dinh huong xu ly
- SQL Agent: sinh va thuc thi truy van du lieu
- Analysis Agent: rut insight tu ket qua
- Visualization Agent: chon loai bieu do phu hop
- Forecast Agent: du bao xu huong
- Anomaly Agent: phat hien diem bat thuong
- Critic Agent: kiem tra cheo, giam sai sot
- Responder Agent: tong hop cau tra loi cuoi cung
""")

st.subheader("Cong nghe su dung")
st.write("LangGraph, LangChain, Groq API, PostgreSQL, FAISS, FastAPI, Streamlit, Docker, GitHub Actions")