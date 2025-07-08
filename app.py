
import streamlit as st
import pandas as pd

# Carregar os dados
df = pd.read_excel("Produtores_SDA.xlsx")

st.title("Dashboard de Produtores SDA")

# Filtros interativos
tecnicos = st.multiselect("Selecione o(s) Técnico(s):", sorted(df["TECNICO"].dropna().unique()))
distritos = st.multiselect("Selecione o(s) Distrito(s):", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.multiselect("Selecione o(s) Comprador(es):", sorted(df["COMPRADOR"].dropna().unique()))

# Aplicar filtros
df_filtrado = df.copy()
if tecnicos:
    df_filtrado = df_filtrado[df_filtrado["TECNICO"].isin(tecnicos)]
if distritos:
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"].isin(distritos)]
if compradores:
    df_filtrado = df_filtrado[df_filtrado["COMPRADOR"].isin(compradores)]

# Exibir dados
st.subheader("Dados Filtrados")
st.dataframe(df_filtrado)
