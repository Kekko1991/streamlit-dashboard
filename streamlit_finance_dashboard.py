
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("📊 Ultra Modern Finance Dashboard")

st.sidebar.header("⚙️ Upload Excel file")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.sidebar.success("File uploaded successfully!")

    st.sidebar.header("🔎 Filters")

    columns = df.columns.str.lower()
    date_col = next((col for col in df.columns if "data" in col.lower()), None)
    amount_col = next((col for col in df.columns if "importo" in col.lower() or "amount" in col.lower()), None)
    supplier_col = next((col for col in df.columns if "fornitore" in col.lower() or "supplier" in col.lower()), None)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input("📅 Date range", [min_date, max_date])
        df = df[(df[date_col] >= pd.to_datetime(date_range[0])) & (df[date_col] <= pd.to_datetime(date_range[1]))]

    if supplier_col:
        suppliers = df[supplier_col].dropna().unique()
        selected_suppliers = st.sidebar.multiselect("🏢 Supplier", options=suppliers, default=list(suppliers))
        df = df[df[supplier_col].isin(selected_suppliers)]

    st.markdown("### 💡 Key Metrics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Total Rows", len(df))
    with col2:
        if amount_col:
            st.metric("💰 Total Amount", f"€ {df[amount_col].sum():,.2f}")
    with col3:
        if amount_col:
            st.metric("📈 Average", f"€ {df[amount_col].mean():,.2f}")

    st.markdown("### 📊 Charts")
    if date_col and amount_col:
        df_grouped = df.groupby(pd.Grouper(key=date_col, freq="M"))[amount_col].sum().reset_index()
        fig = px.line(df_grouped, x=date_col, y=amount_col, title="📆 Monthly Totals")
        st.plotly_chart(fig, use_container_width=True)

    if supplier_col and amount_col:
        df_pie = df.groupby(supplier_col)[amount_col].sum().reset_index()
        fig2 = px.pie(df_pie, values=amount_col, names=supplier_col, title="🏢 Distribution by Supplier")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📋 Data Preview")
    st.dataframe(df, use_container_width=True)

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, index=False, sheet_name="FilteredData")
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    st.download_button(
        label="⬇️ Download filtered data as Excel",
        data=to_excel(df),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Please upload an Excel file to get started.")
