
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apuração PED 2025", layout="wide")
st.title("📊 Resultado Final - PED 2025")

# Carregar dados
df = pd.read_excel("PED 2025 - APURAÇÃO_FINAL.xlsx")

# Filtro por candidato
candidatos = df["CANDIDATO"].dropna().unique()
candidato_sel = st.selectbox("Filtrar por Candidato", ["Todos"] + sorted(candidatos.tolist()))

df_filtrado = df.copy()
if candidato_sel != "Todos":
    df_filtrado = df[df["CANDIDATO"] == candidato_sel]

# Exibir tabela
st.subheader("📋 Tabela completa")
st.dataframe(df_filtrado)

# Gráfico de VOTOS_PRES por CANDIDATO
st.subheader("🗳️ Votos para Presidente por Candidato")
grafico = df_filtrado.groupby("CANDIDATO")["VOTOS_PRES"].sum().sort_values(ascending=False)
st.bar_chart(grafico)

# Total geral
st.subheader("📌 Total de votos para Presidente")
st.metric("Total", int(df_filtrado["VOTOS_PRES"].sum()))
