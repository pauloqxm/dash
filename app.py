
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard SDA", layout="wide")

SENHA_CORRETA = "1234"
st.sidebar.title("🔐 Acesso Restrito")
senha = st.sidebar.text_input("Digite a senha:", type="password")

if senha != SENHA_CORRETA:
    st.warning("Área protegida. Digite a senha correta para acessar.")
    st.stop()

df = pd.read_excel("Produtores_SDA.xlsx")

st.sidebar.title("🔎 Filtros")
tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))

df_filtrado = df.copy()
if tecnicos:
    df_filtrado = df_filtrado[df_filtrado["TECNICO"].isin(tecnicos)]
if distritos:
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"].isin(distritos)]
if compradores:
    df_filtrado = df_filtrado[df_filtrado["COMPRADOR"].isin(compradores)]

st.title("📊 Dashboard de Produtores SDA")
st.markdown("Use os filtros ao lado para explorar os dados dos produtores de forma interativa.")
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")
st.dataframe(df_filtrado, use_container_width=True)
