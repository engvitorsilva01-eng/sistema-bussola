import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ================= CONFIG =================
st.set_page_config(page_title="Sistema Bússola", layout="wide")

USUARIO = "bussola"
SENHA = "2026"

ARQUIVO_LEADS = "leads.csv"
META_VAGAS = 30
DATA_CURSO = date(2026, 5, 20)

# ================= LOGIN =================
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Sistema Bússola")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == USUARIO and senha == SENHA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

# ================= FUNÇÕES =================
def carregar_leads():
    if os.path.exists(ARQUIVO_LEADS):
        return pd.read_csv(ARQUIVO_LEADS)
    else:
        df = pd.DataFrame(columns=["Nome", "Telefone", "Origem", "Status", "Data"])
        df.to_csv(ARQUIVO_LEADS, index=False)
        return df

def salvar_leads(df):
    df.to_csv(ARQUIVO_LEADS, index=False)

# ================= DASHBOARD =================
st.title("📊 Painel da Turma")

leads_df = carregar_leads()

confirmados = len(leads_df[leads_df["Status"] == "Pago"])
vagas_restantes = META_VAGAS - confirmados
taxa_conversao = (confirmados / len(leads_df) * 100) if len(leads_df) > 0 else 0
dias_restantes = (DATA_CURSO - date.today()).days

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎯 Meta", META_VAGAS)
col2.metric("✅ Confirmados", confirmados)
col3.metric("🪑 Restantes", vagas_restantes)
col4.metric("📅 Dias para o curso", dias_restantes)

st.divider()

# ================= CADASTRO =================
st.subheader("➕ Adicionar Lead")

with st.form("form_lead"):
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    origem = st.selectbox("Origem", ["Story", "Reels", "Indicação", "Outro"])
    status = st.selectbox("Status", ["Novo", "Informações enviadas", "Aguardando resposta", "Confirmado", "Pago"])

    enviar = st.form_submit_button("Salvar")

    if enviar:
        nova_linha = {
            "Nome": nome,
            "Telefone": telefone,
            "Origem": origem,
            "Status": status,
            "Data": datetime.now().strftime("%d/%m/%Y")
        }
        leads_df = pd.concat([leads_df, pd.DataFrame([nova_linha])], ignore_index=True)
        salvar_leads(leads_df)
        st.success("Lead salvo com sucesso!")
        st.rerun()

st.divider()

# ================= LISTA =================
st.subheader("📋 Leads cadastrados")

st.dataframe(leads_df, use_container_width=True)

st.divider()

# ================= LOGOUT =================
if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
