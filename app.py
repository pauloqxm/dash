import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apuração PED 2025", layout="wide")

st.title("📊 Resultado Final - PED 2025")

# Carregando planilha
df = pd.read_excel("PED 2025 - APURAÇÃO_FINAL.xlsx")

# Filtros
col1, col2 = st.columns(2)
with col1:
    zonas = df["Zona"].unique()
    zona_selecionada = st.selectbox("Filtrar por Zona:", ["Todas"] + list(zonas))
with col2:
    locais = df["Local"].unique()
    local_selecionado = st.selectbox("Filtrar por Local:", ["Todos"] + list(locais))

# Aplicar filtros
df_filtrado = df.copy()
if zona_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Zona"] == zona_selecionada]
if local_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Local"] == local_selecionado]

# Exibir tabela
st.subheader("📋 Dados detalhados")
st.dataframe(df_filtrado)

# Total de votos por candidato
if "Candidato" in df.columns and "Votos" in df.columns:
    st.subheader("🗳️ Votos por Candidato")
    votos_candidato = df_filtrado.groupby("Candidato")["Votos"].sum().sort_values(ascending=False)
    st.bar_chart(votos_candidato)

# Total geral
st.subheader("📌 Total de Votos")
st.metric("Total", int(df_filtrado["Votos"].sum()))

