import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json

# Configuração do app
st.set_page_config(layout="wide")
st.title("📋 Painel de Acompanhamento de Clientes")

# Autenticação com Google Sheets via secrets
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Nome da planilha e aba
SHEET_NAME = "painel_clientes"
WORKSHEET_NAME = "base"
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Carregar os dados
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Ajustar datas
df["Data do Último Contato"] = pd.to_datetime(df["Data do Último Contato"], errors='coerce')
df["Dias desde o último contato"] = (pd.Timestamp.today().normalize() - df["Data do Último Contato"]).dt.days

# Filtro lateral
st.sidebar.header("🔍 Filtros")
responsaveis = ["Todos"] + sorted(df["Responsável"].dropna().unique().tolist())
filtro_resp = st.sidebar.selectbox("Responsável", responsaveis)

if filtro_resp != "Todos":
    df = df[df["Responsável"] == filtro_resp]

# Listagem principal
st.subheader("📊 Lista de Clientes")
for idx, row in df.iterrows():
    with st.expander(f"📌 {row['Empresa']} - {row['Contato']}"):
        st.write(f"**Email:** {row['Email']}")
        st.write(f"**Telefone:** {row['Telefone']}")
        st.write(f"**Responsável:** {row['Responsável']}")
        st.write(f"**Data do Último Contato:** {row['Data do Último Contato'].strftime('%d/%m/%Y')}")
        st.write(f"**Dias desde o último contato:** {row['Dias desde o último contato']}")

        if st.button("✅ Contatei hoje", key=f"contato_{idx}"):
            # Atualiza o Google Sheets
            nova_data = datetime.today().strftime("%Y-%m-%d")
            row_number = idx + 2  # 1-based + header
            col_index = df.columns.get_loc("Data do Último Contato") + 1
            sheet.update_cell(row_number, col_index, nova_data)
            st.success("✔️ Data atualizada com sucesso.")

# Exportação CSV
st.subheader("📁 Exportar Base Atualizada")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV", data=csv, file_name="clientes_atualizados.csv", mime="text/csv")
