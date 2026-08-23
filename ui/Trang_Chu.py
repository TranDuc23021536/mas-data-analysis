import streamlit as st
from lib.theme import apply_theme
from lib.session_manager import init_session
from lib.api_client import health

st.set_page_config(page_title="MAS Data Analysis", layout="centered")
apply_theme()
init_session()

st.title("Multi-Agent Data Analysis System")
st.write("He thong AI da tac tu ho tro phan tich du lieu kinh doanh bang ngon ngu tu nhien.")

if health():
    st.success("Backend dang hoat dong")
else:
    st.error("Khong ket noi duoc backend, kiem tra lai API")

st.markdown("---")
st.subheader("Cac trang chuc nang")
st.write("- Tro chuyen: dat cau hoi phan tich du lieu")
st.write("- Dashboard: tong quan so lieu kinh doanh")
st.write("- San pham: danh muc san pham hien co")
st.write("- Gioi thieu: thong tin ve he thong")

st.info("Chon trang o thanh dieu huong ben trai de bat dau.")