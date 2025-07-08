
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard SDA", layout="wide")

df = pd.read_excel("Produtores_SDA.xlsx")

# Processamento da coluna COORDENADAS
df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.split(",", expand=True)
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
df["ORDENHA?"] = df["ORDENHA?"].str.upper().fillna("NAO")
df["INSEMINA?"] = df["INSEMINA?"].str.upper().fillna("NAO")

# Sidebar - Filtros
st.sidebar.title("🔎 Filtros")
tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))
produtor = st.sidebar.text_input("🔍 Buscar Produtor")

# Aplicar filtros cruzados
df_filtrado = df.copy()
if tecnicos:
    df_filtrado = df_filtrado[df_filtrado["TECNICO"].isin(tecnicos)]
if distritos:
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"].isin(distritos)]
if compradores:
    df_filtrado = df_filtrado[df_filtrado["COMPRADOR"].isin(compradores)]
if produtor:
    df_filtrado = df_filtrado[df_filtrado["PRODUTOR"].str.contains(produtor, case=False, na=False)]

# Tabela no topo
st.title("📋 Dados dos Produtores")
st.dataframe(df_filtrado, use_container_width=True)
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")

# Gráficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("✅ Ordenha")
    st.bar_chart(df_filtrado["ORDENHA?"].value_counts())

with col2:
    st.subheader("🧬 Insemina")
    st.bar_chart(df_filtrado["INSEMINA?"].value_counts())

# Mapa
st.subheader("🗺️ Localização dos Produtores")
df_mapa = df_filtrado.dropna(subset=["LATITUDE", "LONGITUDE"])
st.map(df_mapa.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon"}), zoom=10)
