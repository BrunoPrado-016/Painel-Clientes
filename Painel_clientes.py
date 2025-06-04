import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

st.set_page_config(layout="wide")
st.title("📋 Acompanhamento de Clientes")

uploaded_file = st.file_uploader("Upload de Planilha (.xlsx)", type=["xlsx"])

def highlight_row(row):
    days_since = (datetime.today().date() - row['Data do Último Contato'].date()).days
    if days_since == 30:
        return ['background-color: yellow'] * len(row)
    elif days_since > 30:
        return ['background-color: lightcoral'] * len(row)
    else:
        return [''] * len(row)

def send_email_alert(df_filtrado, vendedor, email_destino):
    clientes = df_filtrado[df_filtrado["Responsável"] == vendedor]
    clientes = clientes[clientes["Dias desde o último contato"] >= 30]
    if clientes.empty:
        return

    corpo = "Olá,\n\nEstes são os clientes com 30 dias ou mais sem contato:\n"
    for _, row in clientes.iterrows():
        corpo += f"- {row['Nome']} da empresa {row['Empresa']} (último contato: {row['Data do Último Contato'].strftime('%d/%m/%Y')})\n"

    corpo += "\nFavor realizar o follow-up.\n"
    msg = MIMEText(corpo)
    msg["Subject"] = "Lembrete de Follow-Up"
    msg["From"] = "seuemail@gmail.com"
    msg["To"] = email_destino

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("seuemail@gmail.com", "sua_senha")
        server.send_message(msg)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    df['Data do Último Contato'] = pd.to_datetime(df['Data do Último Contato'], errors='coerce')
    df["Dias desde o último contato"] = (datetime.today().date() - df["Data do Último Contato"].dt.date).dt.days

    st.subheader("📊 Base de Clientes")
    filtro = st.selectbox("Responsável", options=["Todos"] + sorted(df["Responsável"].dropna().unique().tolist()))

    if filtro != "Todos":
        df = df[df["Responsável"] == filtro]

    busca = st.text_input("🔍 Buscar por nome ou empresa")
    if busca:
        df = df[df["Nome"].str.contains(busca, case=False) | df["Empresa"].str.contains(busca, case=False)]

    df_visual = df[["Nome", "Empresa", "Responsável", "Data do Último Contato", "Dias desde o último contato"]].copy()
    st.dataframe(df_visual.style.apply(highlight_row, axis=1), use_container_width=True)

    if st.button("📧 Enviar alertas por e-mail"):
        vendedores = df["Responsável"].unique()
        for vendedor in vendedores:
            email = st.text_input(f"Email do {vendedor}", key=vendedor)
            if email:
                send_email_alert(df, vendedor, email)
                st.success(f"E-mail enviado para {vendedor}")
