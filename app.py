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

DATA_ONLINE_INICIO = date(2026, 5, 16)
DATA_PRATICA_INICIO = date(2026, 5, 23)

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

dias_online = (DATA_ONLINE_INICIO - date.today()).days
dias_pratica = (DATA_PRATICA_INICIO - date.today()).days

ocupacao = confirmados / META_VAGAS if META_VAGAS > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("🎯 Meta de Vagas", META_VAGAS)
col2.metric("✅ Confirmados", confirmados)
col3.metric("🪑 Restantes", vagas_restantes)

st.progress(ocupacao)

col4, col5, col6 = st.columns(3)

col4.metric("💻 Online inicia em", dias_online)
col5.metric("🏥 Prática inicia em", dias_pratica)
col6.metric("📈 Taxa de Conversão (%)", f"{taxa_conversao:.1f}")

# Alertas
if dias_online <= 30 and dias_online > 0:
    st.warning("⚠️ Faltam menos de 30 dias para as aulas online!")

if dias_pratica <= 30 and dias_pratica > 0:
    st.warning("⚠️ Faltam menos de 30 dias para as aulas práticas!")

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

if not leads_df.empty:
    st.dataframe(leads_df, use_container_width=True)
else:
    st.info("Nenhum lead cadastrado ainda.")

st.divider()

# ================= LOGOUT =================
if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
