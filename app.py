import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ================= CONFIG =================
st.set_page_config(page_title="Sistema Bússola", layout="wide")

USUARIO = "bussola"
SENHA = "2026"

ARQUIVO_LEADS = "leads.csv"
META_VAGAS = 25

VALOR_TEORICO = 97
VALOR_PRATICA = 397

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
        df = pd.DataFrame(columns=["Nome", "Telefone", "Origem", "Status", "Modalidade", "Data"])
        df.to_csv(ARQUIVO_LEADS, index=False)
        return df

def salvar_leads(df):
    df.to_csv(ARQUIVO_LEADS, index=False)

# ================= DASHBOARD =================
st.title("📊 Painel da Turma")

leads_df = carregar_leads()

# Garantir coluna Modalidade se vier de versão antiga
if "Modalidade" not in leads_df.columns:
    leads_df["Modalidade"] = ""

confirmados_df = leads_df[leads_df["Status"] == "Pago"]

qtd_teorico = len(confirmados_df[confirmados_df["Modalidade"] == "Teórico"])
qtd_pratica = len(confirmados_df[confirmados_df["Modalidade"] == "Prática"])

total_confirmados = len(confirmados_df)
vagas_restantes = META_VAGAS - total_confirmados

# Receita
receita_teorico = qtd_teorico * VALOR_TEORICO
receita_pratica = qtd_pratica * VALOR_PRATICA
receita_total = receita_teorico + receita_pratica
receita_potencial_max = META_VAGAS * VALOR_PRATICA

# Datas
dias_online = (DATA_ONLINE_INICIO - date.today()).days
dias_pratica = (DATA_PRATICA_INICIO - date.today()).days

ocupacao = total_confirmados / META_VAGAS if META_VAGAS > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("🎯 Meta de Alunos", META_VAGAS)
col2.metric("✅ Confirmados", total_confirmados)
col3.metric("🪑 Restantes", vagas_restantes)

st.progress(ocupacao)

col4, col5 = st.columns(2)
col4.metric("💻 Online inicia em", dias_online)
col5.metric("🏥 Prática inicia em", dias_pratica)

st.divider()

# ================= MODALIDADES =================
st.subheader("📘 Distribuição de Alunos")

col6, col7 = st.columns(2)
col6.metric("Teórico (97)", qtd_teorico)
col7.metric("Prática (397)", qtd_pratica)

st.divider()

# ================= FINANCEIRO =================
st.subheader("💰 Financeiro")

col8, col9 = st.columns(2)
col8.metric("💵 Receita Total", f"R$ {receita_total:,.2f}")
col9.metric("📈 Receita Potencial Máxima", f"R$ {receita_potencial_max:,.2f}")

st.divider()

# ================= CADASTRO =================
st.subheader("➕ Adicionar Lead")

with st.form("form_lead"):
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    origem = st.selectbox("Origem", ["Story", "Reels", "Indicação", "Outro"])
    status = st.selectbox("Status", ["Novo", "Informações enviadas", "Aguardando resposta", "Confirmado", "Pago"])
    modalidade = st.selectbox("Modalidade", ["Teórico", "Prática"])

    enviar = st.form_submit_button("Salvar")

    if enviar:
        nova_linha = {
            "Nome": nome,
            "Telefone": telefone,
            "Origem": origem,
            "Status": status,
            "Modalidade": modalidade,
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
