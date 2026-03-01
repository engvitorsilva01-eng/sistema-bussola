import streamlit as st
import pandas as pd
from datetime import datetime

# ===== CONFIG =====
st.set_page_config(page_title="Sistema Bússola", layout="wide")

# ===== LOGIN SIMPLES =====
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Sistema Bússola - Login")

        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user == "bussola" and password == "2026":
                st.session_state.logged_in = True
                st.success("Login realizado!")
            else:
                st.error("Usuário ou senha incorretos")
        return False
    return True

if not check_login():
    st.stop()

# ===== DASHBOARD =====
st.title("📊 Painel da Turma")

meta_vagas = 30
matriculas = st.number_input("Matrículas confirmadas", min_value=0, max_value=100, value=0)
vagas_restantes = meta_vagas - matriculas

col1, col2, col3 = st.columns(3)

col1.metric("🎯 Meta de Vagas", meta_vagas)
col2.metric("✅ Confirmadas", matriculas)
col3.metric("🪑 Restantes", vagas_restantes)

st.divider()

# ===== CRM =====
st.subheader("👥 Cadastro de Leads")

if "leads" not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=["Nome", "Telefone", "Status", "Data"])

nome = st.text_input("Nome do Lead")
telefone = st.text_input("Telefone")
status = st.selectbox("Status", ["Novo", "Informações enviadas", "Aguardando resposta", "Confirmado", "Pago"])

if st.button("Adicionar Lead"):
    nova_linha = {
        "Nome": nome,
        "Telefone": telefone,
        "Status": status,
        "Data": datetime.now().strftime("%d/%m/%Y")
    }
    st.session_state.leads = pd.concat([st.session_state.leads, pd.DataFrame([nova_linha])], ignore_index=True)
    st.success("Lead adicionado!")

st.dataframe(st.session_state.leads)
