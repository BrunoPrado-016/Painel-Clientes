import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📋 Acompanhamento de Clientes Ativos")

uploaded_file = st.file_uploader("📎 Faça upload da planilha (.xlsx)", type=["xlsx"])

def highlight_row(row):
    dias = row["Dias desde o último contato"]
    if dias == 30:
        return ['background-color: yellow'] * len(row)
    elif dias > 30:
        return ['background-color: lightcoral'] * len(row)
    else:
        return [''] * len(row)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Garantir colunas corretas
        colunas_esperadas = ["Empresa", "Contato", "Email", "Telefone", "Responsável", "Data do Último Contato"]
        if not all(col in df.columns for col in colunas_esperadas):
            st.error("⚠️ A planilha precisa conter as seguintes colunas: Empresa, Contato, Email, Telefone, Responsável, Data do Último Contato")
        else:
            # Tratamento de datas
            df["Data do Último Contato"] = pd.to_datetime(df["Data do Último Contato"], errors='coerce')
            df["Dias desde o último contato"] = (datetime.today().date() - df["Data do Último Contato"].dt.date).dt.days

            # Filtro por responsável
            st.sidebar.subheader("🔎 Filtros")
            responsaveis = ["Todos"] + sorted(df["Responsável"].dropna().unique().tolist())
            filtro_resp = st.sidebar.selectbox("Responsável", responsaveis)

            if filtro_resp != "Todos":
                df = df[df["Responsável"] == filtro_resp]

            # Exibição com destaque
            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
else:
    st.info("Envie uma planilha .xlsx com colunas: Empresa, Contato, Email, Telefone, Responsável, Data do Último Contato.")