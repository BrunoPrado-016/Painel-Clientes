import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📋 Acompanhamento de Clientes Ativos")

st.markdown("Faça upload de uma planilha `.xlsx` com os campos: Empresa, Contato, Email, Telefone, Responsável e Data do Último Contato.")

uploaded_file = st.file_uploader("📎 Upload da planilha de clientes", type=["xlsx"])

if "df" not in st.session_state:
    st.session_state.df = None

def highlight_row(row):
    dias = row["Dias desde o último contato"]
    if dias == 30:
        return ['background-color: yellow'] * len(row)
    elif dias > 30:
        return ['background-color: lightcoral'] * len(row)
    else:
        return ['background-color: lightgreen'] * len(row)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        colunas_esperadas = ["Empresa", "Contato", "Email", "Telefone", "Responsável", "Data do Último Contato"]
        if not all(col in df.columns for col in colunas_esperadas):
            st.error("⚠️ A planilha deve conter as colunas: " + ", ".join(colunas_esperadas))
        else:
            df["Data do Último Contato"] = pd.to_datetime(df["Data do Último Contato"], errors="coerce")
            df["Dias desde o último contato"] = (
                pd.Timestamp.today().normalize() - df["Data do Último Contato"]
            ).dt.days

            st.session_state.df = df

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")

if st.session_state.df is not None:
    df = st.session_state.df

    st.sidebar.header("🔎 Filtros")
    responsaveis = ["Todos"] + sorted(df["Responsável"].dropna().unique().tolist())
    filtro_resp = st.sidebar.selectbox("Responsável", responsaveis)

    if filtro_resp != "Todos":
        df = df[df["Responsável"] == filtro_resp]

    st.subheader("📊 Lista de Clientes")
    for idx, row in df.iterrows():
        with st.expander(f"📌 {row['Empresa']} - {row['Contato']}"):
            st.write(f"**Email:** {row['Email']}")
            st.write(f"**Telefone:** {row['Telefone']}")
            st.write(f"**Responsável:** {row['Responsável']}")
            st.write(f"**Data do Último Contato:** {row['Data do Último Contato'].strftime('%d/%m/%Y')}")
            st.write(f"**Dias desde o último contato:** {row['Dias desde o último contato']}")

            if st.button(f"✅ Contatei hoje", key=f"update_{idx}"):
                st.session_state.df.at[idx, "Data do Último Contato"] = pd.Timestamp.today().normalize()
                st.session_state.df["Dias desde o último contato"] = (
                    pd.Timestamp.today().normalize() - st.session_state.df["Data do Último Contato"]
                ).dt.days
                st.success(f"Contato atualizado para hoje ({datetime.today().strftime('%d/%m/%Y')})")

    st.subheader("📁 Exportar base atualizada")
    output = BytesIO()
    st.session_state.df.to_excel(output, index=False, engine="openpyxl")
    st.download_button(
        label="📥 Baixar planilha atualizada",
        data=output.getvalue(),
        file_name="clientes_atualizados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
