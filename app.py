
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="📅 Programação Geral - Banabuiú", layout="wide")
st.title("📅 Programação de Atividades - Gerência Banabuiú")

# Carregar dados
df = pd.read_excel("PROGRAM_GRBANABUIU.xlsx")
df.columns = [col.strip().upper() for col in df.columns]

# Ajustes de tipo de dado
df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
df['DIA'] = df['DATA'].dt.strftime('%d/%m/%Y')
df = df.dropna(subset=['DATA'])

# Adiciona coluna de mês em português
nomes_meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
df["MÊS"] = df["DATA"].dt.month.map(nomes_meses)

# Abas
aba = st.sidebar.radio("Navegar por:", ["📊 Visão Geral", "📍 Atividades", "🚗 Logística", "🗺️ Mapa (experimental)"])

# Filtros comuns
st.sidebar.markdown("### Filtros")
meses = df["MÊS"].dropna().unique().tolist()
datas = df['DIA'].unique().tolist()
eixos = df['EIXO'].dropna().unique().tolist()
nucleos = df['NÚCLEO'].dropna().unique().tolist()
formatos = df['FORMATO'].dropna().unique().tolist()

filtro_mes = st.sidebar.selectbox("Mês", sorted(meses))
filtro_data = df[df["MÊS"] == filtro_mes]['DIA'].unique().tolist()
filtro_data = st.sidebar.multiselect("Data", filtro_data, default=filtro_data)
filtro_eixo = st.sidebar.multiselect("Eixo", eixos, default=eixos)
filtro_nucleo = st.sidebar.multiselect("Núcleo", nucleos, default=nucleos)
filtro_formato = st.sidebar.multiselect("Formato", formatos, default=formatos)

# Aplicar filtros
df_filtrado = df[
    (df["MÊS"] == filtro_mes) &
    df['DIA'].isin(filtro_data) &
    df['EIXO'].isin(filtro_eixo) &
    df['NÚCLEO'].isin(filtro_nucleo) &
    df['FORMATO'].isin(filtro_formato)
]

# Aba 1: Visão Geral
if aba == "📊 Visão Geral":
    st.subheader("📌 Quantidade de Atividades por Eixo")
    eixo_count = df_filtrado['EIXO'].value_counts()
    st.bar_chart(eixo_count)

    st.subheader("📌 Quantidade por Núcleo")
    nucleo_count = df_filtrado['NÚCLEO'].value_counts()
    st.bar_chart(nucleo_count)

    st.subheader("📌 Formatos utilizados")
    formato_count = df_filtrado['FORMATO'].value_counts()
    st.bar_chart(formato_count)

# Aba 2: Atividades
elif aba == "📍 Atividades":
    st.subheader("📍 Lista de Atividades Programadas")
    st.dataframe(df_filtrado[['DIA', 'GERÊNCIA', 'NÚCLEO', 'EIXO', 'ATIVIDADE', 'FORMATO', 'RESPONSÁVEIS', 'LOCAL']])

# Aba 3: Logística
elif aba == "🚗 Logística":
    st.subheader("🚗 Logística e Diárias")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Km previstos", f"{df_filtrado['PREVISÃO_KM'].sum():.0f} km")
    col2.metric("Diárias Motorista", int(df_filtrado['DIARIA_MOT'].fillna(0).sum()))
    col3.metric("Diárias Terceiro", int(df_filtrado['DIARIA_TER'].fillna(0).sum()))
    st.dataframe(df_filtrado[['DIA', 'VEÍCULO', 'PREVISÃO_KM', 'DIARIA_MOT', 'DIARIA_TER', 'DIARIA_C&C']])

# Aba 4: Mapa
elif aba == "🗺️ Mapa (experimental)":
    st.subheader("🗺️ Mapa (baseado no campo LOCAL)")
    mapa_df = df_filtrado[['LOCAL', 'DATA', 'ATIVIDADE']].dropna()
    if not mapa_df.empty:
        st.dataframe(mapa_df)
        st.info("Este mapa é simbólico, pois o campo 'LOCAL' não possui coordenadas. Para ativar mapa real, adicione colunas de latitude/longitude.")
    else:
        st.warning("Nenhum local definido nas atividades filtradas.")
