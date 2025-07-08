
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apuração PED 2025", layout="wide")
st.title("📊 Dashboard Interativo - PED 2025")

# Carregar dados
df = pd.read_excel("PED 2025 - APURAÇÃO_FINAL.xlsx")

# Converter colunas para maiúsculas sem acento (garantia)
df.columns = [col.strip().upper() for col in df.columns]

# Abas
aba = st.sidebar.radio("Escolha a visualização:", ["📋 Tabela", "🗳️ Votos por Candidato", "📦 Votos por Chapa", "📌 Totais"])

# Filtros (colocados no sidebar)
with st.sidebar:
    st.markdown("### Filtros")
    candidatos = df["CANDIDATO"].dropna().unique()
    filtro_candidato = st.multiselect("Filtrar Candidatos", candidatos, default=candidatos)

    chapas = df["NOME_CHAPA"].dropna().unique()
    filtro_chapa = st.multiselect("Filtrar Chapas", chapas, default=chapas)

# Aplicar filtros
df_filtrado = df[
    df["CANDIDATO"].isin(filtro_candidato) &
    df["NOME_CHAPA"].isin(filtro_chapa)
]

# Tabela
if aba == "📋 Tabela":
    st.subheader("📋 Tabela completa com filtros aplicados")
    st.dataframe(df_filtrado)

# Gráfico de votos por candidato
elif aba == "🗳️ Votos por Candidato":
    st.subheader("🗳️ Comparativo de Votos para Presidente por Candidato")
    votos = df_filtrado.groupby("CANDIDATO")["VOTOS_PRES"].sum().sort_values(ascending=False)
    st.bar_chart(votos)

# Gráfico de votos por chapa
elif aba == "📦 Votos por Chapa":
    st.subheader("📦 Comparativo de Votos por Chapa")
    votos_chapa = df_filtrado.groupby("NOME_CHAPA")["VOTO_CHAPA"].sum().sort_values(ascending=False)
    st.bar_chart(votos_chapa)

# Totais
elif aba == "📌 Totais":
    total_pres = int(df_filtrado["VOTOS_PRES"].sum())
    total_chapa = int(df_filtrado["VOTO_CHAPA"].sum())
    col1, col2 = st.columns(2)
    col1.metric("Total de Votos para Presidente", total_pres)
    col2.metric("Total de Votos para Chapas", total_chapa)
