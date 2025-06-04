import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(layout="wide")
st.title("📋 Acompanhamento de Clientes")

# Upload da planilha
uploaded_file = st.file_uploader("Faça upload da planilha de clientes (.xlsx)", type=["xlsx"])

def highlight_row(row):
    dias = row['Dias desde o último contato']
    if dias == 30:
        return ['background-color: yellow'] * len(row)
    elif dias > 30:
        return ['background-color: lightcoral'] * len(row)
    else:
        return [''] * len(row)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Conversão de data
        df['Data do Último Contato'] = pd.to_datetime(df['Data do Último Contato'], errors='coerce')

        # Cálculo de dias desde o último contato
        df["Dias desde o último contato"] = (
            datetime.today().date() - df["Data do Último Contato"].dt.date
        ).dt.days

        # Exibição com destaque por status
        st.subheader("📊 Clientes")
        st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler a planilha: {e}")
else:
    st.info("Envie uma planilha .xlsx contendo as colunas: Nome, Empresa, Responsável, Data do Último Contato")
