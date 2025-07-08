
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apuração PED 2025", layout="wide")
st.title("📊 Resultado Final - PED 2025")

# Carregar dados
df = pd.read_excel("PED 2025 - APURAÇÃO_FINAL.xlsx")

# Exibir tabela completa
st.subheader("📋 Tabela completa")
st.dataframe(df)

# Gráfico de VOTOS_PRES por CANDIDATO
st.subheader("🗳️ Comparativo de Votos para Presidente por Candidato")
grafico = df.groupby("CANDIDATO")["VOTOS_PRES"].sum().sort_values(ascending=False)
st.bar_chart(grafico)

# Total geral
st.subheader("📌 Total de votos para Presidente")
st.metric("Total", int(df["VOTOS_PRES"].sum()))
