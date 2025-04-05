
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="💼 Finance Dashboard", layout="wide")

# HEADER
st.markdown("<h1 style='font-size: 36px; color: #00BFFF;'>💼 Finance Dashboard con Schede e Modifica</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #00BFFF;'>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color:#00BFFF'>📂 Caricamento File</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Carica un file Excel", type=["xlsx"])
    st.markdown("---")
    st.markdown("<h3 style='color:#00BFFF'>🔍 Filtri</h3>", unsafe_allow_html=True)

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

    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["📊 KPI + Grafici", "📋 Dati", "✏️ Modifica", "⬇️ Esportazione"])

    with tab1:
        st.subheader("📊 KPI Principali")
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("📄 Numero righe", len(df))
        with kpi2:
            if amount_col:
                st.metric("💰 Totale importi", f"€ {df[amount_col].sum():,.2f}")
        with kpi3:
            if amount_col:
                st.metric("📈 Media importi", f"€ {df[amount_col].mean():,.2f}")

        st.markdown("<hr style='border: 1px solid #00BFFF;'>", unsafe_allow_html=True)

        if date_col and amount_col:
            st.subheader("📆 Totali mensili")
            df_grouped = df.groupby(pd.Grouper(key=date_col, freq='M'))[amount_col].sum().reset_index()
            fig1 = px.line(df_grouped, x=date_col, y=amount_col, markers=True, template="plotly_dark", title="Andamento mensile")
            fig1.update_traces(line_color='#00BFFF')
            st.plotly_chart(fig1, use_container_width=True)

        if supplier_col and amount_col:
            st.subheader("🏢 Distribuzione per fornitore")
            df_pie = df.groupby(supplier_col)[amount_col].sum().reset_index()
            fig2 = px.pie(df_pie, values=amount_col, names=supplier_col, title="Fornitori", hole=0.4)
            fig2.update_traces(textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📋 Anteprima dei dati filtrati")
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("✏️ Modifica diretta dei dati")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True, resizable=True)
        grid_options = gb.build()
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            theme="alpine",
            enable_enterprise_modules=False
        )
        edited_df = grid_response['data']
        st.success("✅ Modifiche applicate! Puoi esportarle nella sezione successiva.")

    with tab4:
        st.subheader("⬇️ Esporta i dati")
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='DatiFiltrati')
            writer.close()
            return output.getvalue()

        st.download_button(
            label="⬇️ Scarica Excel con modifiche",
            data=to_excel(edited_df),
            file_name="dati_modificati.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("📂 Carica un file Excel per iniziare.")
