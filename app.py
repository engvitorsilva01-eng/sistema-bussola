import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

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
def carregar_dados():
    if os.path.exists(ARQUIVO_LEADS):
        df = pd.read_csv(ARQUIVO_LEADS)
    else:
        df = pd.DataFrame(columns=[
            "Nome", "Telefone", "Origem",
            "Modalidade", "Valor Cheio",
            "Valor Pago", "Saldo",
            "Forma Pagamento",
            "Status Financeiro",
            "Data"
        ])
        df.to_csv(ARQUIVO_LEADS, index=False)

    # Garantir colunas caso venha de versão antiga
    colunas_necessarias = [
        "Nome", "Telefone", "Origem",
        "Modalidade", "Valor Cheio",
        "Valor Pago", "Saldo",
        "Forma Pagamento",
        "Status Financeiro",
        "Data"
    ]

    for col in colunas_necessarias:
        if col not in df.columns:
            df[col] = ""

    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_LEADS, index=False)

# ================= DASHBOARD =================
st.title("📊 Painel da Turma")

df = carregar_dados()

# Conversões financeiras
df["Valor Pago"] = pd.to_numeric(df["Valor Pago"], errors="coerce").fillna(0)
df["Valor Cheio"] = pd.to_numeric(df["Valor Cheio"], errors="coerce").fillna(0)

receita_recebida = df["Valor Pago"].sum()
receita_prevista = df["Valor Cheio"].sum()
total_pendente = receita_prevista - receita_recebida

confirmados = len(df[df["Status Financeiro"] == "Pago"])
vagas_restantes = META_VAGAS - confirmados

dias_online = (DATA_ONLINE_INICIO - date.today()).days
dias_pratica = (DATA_PRATICA_INICIO - date.today()).days

# ================= MÉTRICAS =================
col1, col2, col3 = st.columns(3)
col1.metric("🎯 Meta de Alunos", META_VAGAS)
col2.metric("✅ Pagos", confirmados)
col3.metric("🪑 Restantes", vagas_restantes)

st.divider()

col4, col5 = st.columns(2)
col4.metric("💻 Online inicia em", dias_online)
col5.metric("🏥 Prática inicia em", dias_pratica)

st.divider()

# ================= FINANCEIRO =================
st.subheader("💰 Financeiro")

col6, col7, col8 = st.columns(3)
col6.metric("💵 Receita Recebida", f"R$ {receita_recebida:,.2f}")
col7.metric("📈 Receita Prevista", f"R$ {receita_prevista:,.2f}")
col8.metric("⏳ Total Pendente", f"R$ {total_pendente:,.2f}")

st.divider()

# ================= CADASTRO =================
st.subheader("➕ Adicionar Aluno")

with st.form("form_aluno"):
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    origem = st.selectbox("Origem", ["Story", "Reels", "Indicação", "Outro"])
    modalidade = st.selectbox("Modalidade", ["Teórico", "Prática"])

    valor_cheio = VALOR_TEORICO if modalidade == "Teórico" else VALOR_PRATICA
    valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, step=10.0)

    forma_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Dinheiro"])
    status_financeiro = st.selectbox("Status Financeiro", ["Pago", "Parcial", "Pendente"])

    enviar = st.form_submit_button("Salvar")

    if enviar:
        saldo = valor_cheio - valor_pago

        nova_linha = {
            "Nome": nome,
            "Telefone": telefone,
            "Origem": origem,
            "Modalidade": modalidade,
            "Valor Cheio": valor_cheio,
            "Valor Pago": valor_pago,
            "Saldo": saldo,
            "Forma Pagamento": forma_pagamento,
            "Status Financeiro": status_financeiro,
            "Data": datetime.now().strftime("%d/%m/%Y")
        }

        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        salvar_dados(df)
        st.success("Aluno salvo com sucesso!")
        st.rerun()

st.divider()

# ================= TABELA =================
st.subheader("📋 Alunos cadastrados")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum aluno cadastrado ainda.")

st.divider()

# ================= GERAR PDF =================
st.subheader("📄 Exportar Relatório")

if st.button("Gerar PDF Resumo da Turma"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>RELATÓRIO - TURMA 2026</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    resumo_data = [
        ["Meta de Alunos", META_VAGAS],
        ["Pagos", confirmados],
        ["Vagas Restantes", vagas_restantes],
        ["Receita Recebida", f"R$ {receita_recebida:,.2f}"],
        ["Receita Prevista", f"R$ {receita_prevista:,.2f}"],
        ["Total Pendente", f"R$ {total_pendente:,.2f}"],
        ["Online inicia em", f"{dias_online} dias"],
        ["Prática inicia em", f"{dias_pratica} dias"],
    ]

    tabela_resumo = Table(resumo_data, colWidths=[3 * inch, 2 * inch])
    tabela_resumo.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    elements.append(tabela_resumo)
    elements.append(Spacer(1, 0.5 * inch))

    if not df.empty:
        elements.append(Paragraph("<b>Lista de Alunos</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        dados_alunos = [df.columns.tolist()] + df.values.tolist()

        tabela_alunos = Table(dados_alunos, repeatRows=1)
        tabela_alunos.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7)
        ]))

        elements.append(tabela_alunos)

    doc.build(elements)
    buffer.seek(0)

    st.download_button(
        label="Baixar PDF",
        data=buffer,
        file_name="relatorio_turma_2026.pdf",
        mime="application/pdf"
    )

st.divider()

# ================= LOGOUT =================
if st.button("Sair"):
    st.session_state.logado = False
    st.rerun()
