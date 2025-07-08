
import streamlit as st
import pandas as pd

# Configurações iniciais
st.set_page_config(page_title="Dashboard SDA", layout="wide")

# Carregando os dados
df = pd.read_excel("Produtores_SDA.xlsx")

# Sidebar com filtros
st.sidebar.title("🔎 Filtros")
tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))

# Aplicar filtros
df_filtrado = df.copy()
if tecnicos:
    df_filtrado = df_filtrado[df_filtrado["TECNICO"].isin(tecnicos)]
if distritos:
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"].isin(distritos)]
if compradores:
    df_filtrado = df_filtrado[df_filtrado["COMPRADOR"].isin(compradores)]

# Layout principal
st.title("📊 Dashboard de Produtores SDA")
st.markdown("Use os filtros ao lado para explorar os dados dos produtores de forma interativa.")

# Exibir número de registros encontrados
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")

# Mostrar tabela com os dados filtrados
st.dataframe(df_filtrado, use_container_width=True)
