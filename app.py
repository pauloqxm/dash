
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apuração PED 2025", layout="wide")

st.title("📊 Resultado Final - PED 2025")

uploaded_file = "PED 2025 - APURAÇÃO_FINAL.xlsx"
df = pd.read_excel(uploaded_file)

st.dataframe(df)

# Exemplo de gráfico
if 'Zona' in df.columns and 'Votos' in df.columns:
    zona_votos = df.groupby("Zona")["Votos"].sum().reset_index()
    st.bar_chart(zona_votos.set_index("Zona"))
