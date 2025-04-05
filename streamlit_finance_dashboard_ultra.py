
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="💼 Finance Dashboard", layout="wide")

# HEADER CON LOGO E TITOLO
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Logo_Streamlit.svg/512px-Logo_Streamlit.svg.png", width=70)
with col_title:
    st.markdown("""<h1 style='font-size: 36px; color: #00BFFF;'>Finance Dashboard 💸</h1>""", unsafe_allow_html=True)

st.markdown("""<hr style='border: 1px solid #00BFFF;'>""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""<h3 style='color:#00BFFF'>⚙️ Upload Excel</h3>""", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Carica un file Excel", type=["xlsx"])

    st.markdown("""---""")
    st.markdown("""<h3 style='color:#00BFFF'>🔍 Filtri</h3>""", unsafe_allow_html=True)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Auto-detect colonne
    date_col = next((col for col in df.columns if 'data' in col.lower()), None)
    amount_col = next((col for col in df.columns if 'importo' in col.lower() or 'amount' in col.lower()), None)
    supplier_col = next((col for col in df.columns if 'fornitore' in col.lower() or 'supplier' in col.lower()), None)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input("📅 Intervallo date", [min_date, max_date])
        df = df[(df[date_col] >= pd.to_datetime(date_range[0])) & (df[date_col] <= pd.to_datetime(date_range[1]))]

    if supplier_col:
        suppliers = df[supplier_col].dropna().unique()
        selected_suppliers = st.sidebar.multiselect("🏢 Fornitore", options=suppliers, default=list(suppliers))
        df = df[df[supplier_col].isin(selected_suppliers)]

    # KPI CARDS
    st.markdown("""<h2 style='color:#00BFFF;'>📊 KPI Principali</h2>""", unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("📄 Numero righe", len(df))
    with kpi2:
        if amount_col:
            st.metric("💰 Totale importi", f"€ {df[amount_col].sum():,.2f}")
    with kpi3:
        if amount_col:
            st.metric("📈 Media importi", f"€ {df[amount_col].mean():,.2f}")

    st.markdown("""<hr style='border: 1px solid #00BFFF;'>""", unsafe_allow_html=True)

    # GRAFICI
    st.subheader("📆 Totali mensili")
    if date_col and amount_col:
        df_grouped = df.groupby(pd.Grouper(key=date_col, freq='M'))[amount_col].sum().reset_index()
        fig1 = px.line(df_grouped, x=date_col, y=amount_col, markers=True, template="plotly_dark", title="Andamento mensile")
        fig1.update_traces(line_color='#00BFFF')
        st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🏢 Distribuzione per fornitore")
    if supplier_col and amount_col:
        df_pie = df.groupby(supplier_col)[amount_col].sum().reset_index()
        fig2 = px.pie(df_pie, values=amount_col, names=supplier_col, title="Fornitori", hole=0.4)
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Anteprima dei dati filtrati")
    st.dataframe(df, use_container_width=True)

    # ESPORTAZIONE EXCEL
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='DatiFiltrati')
        writer.close()
        return output.getvalue()

    st.download_button(
        label="⬇️ Scarica Excel filtrato",
        data=to_excel(df),
        file_name="dati_filtrati.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("📂 Carica un file Excel per iniziare.")
