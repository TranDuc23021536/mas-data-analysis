import streamlit as st
import pandas as pd
from lib.theme import apply_theme
from lib.api_client import get_dashboard_summary

st.set_page_config(page_title="Dashboard", layout="centered")
apply_theme()

st.title("Dashboard tong quan")

try:
    data = get_dashboard_summary()

    col1, col2 = st.columns(2)
    col1.metric("Tong doanh thu", f"${data['total_revenue']:.2f}")
    col2.metric("Danh muc ban chay nhat", data.get("top_category") or "N/A")

    st.subheader("So luong ban ghi theo bang")
    counts_df = pd.DataFrame(
        list(data["table_counts"].items()), columns=["Bang", "So dong"]
    )
    st.bar_chart(counts_df.set_index("Bang"))
    st.dataframe(counts_df, use_container_width=True)

except Exception as e:
    st.error(f"Khong tai duoc du lieu dashboard: {e}")