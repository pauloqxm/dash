
import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

st.set_page_config(page_title="📖 Programação ADTC", layout="wide")
st.title("📖 Programação de Cultos - ADTC")

# Carregar dados
df = pd.read_excel("ADTC_PROGRAMAÇÃO.xlsx")
df.columns = [col.strip().upper() for col in df.columns]

# Adicionar coluna de mês (simulada a partir de data se existisse)
# Aqui criamos uma data fictícia associada ao dia da semana
dias_map = {
    "Domingo": 7, "Segunda-Feira": 1, "Terça-Feira": 2,
    "Quarta-Feira": 3, "Quinta-Feira": 4, "Sexta-Feira": 5, "Sábado": 6
}
df["DIA_NUM"] = df["DIA"].map(dias_map)
df["DATA_FICTICIA"] = pd.to_datetime("2025-07-01") + pd.to_timedelta(df["DIA_NUM"] - 1, unit='d')
df["MÊS"] = df["DATA_FICTICIA"].dt.month_name(locale="pt_BR")

# Separar latitude e longitude
df[['LAT', 'LON']] = df['COORDENADAS'].str.split(',', expand=True)
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')

# Filtros
meses = df["MÊS"].unique().tolist()
dias = df['DIA'].unique().tolist()
cultos = df['CULTO'].unique().tolist()
congs = df['CONGREGAÇÃO'].unique().tolist()

st.sidebar.header("Filtros")
filtro_mes = st.sidebar.selectbox("Mês", sorted(meses))
filtro_dia = st.sidebar.multiselect("Dia da semana", dias, default=dias)
filtro_culto = st.sidebar.multiselect("Tipo de culto", cultos, default=cultos)
filtro_cong = st.sidebar.multiselect("Congregação", congs, default=congs)

# Aplicar filtros
df_filtrado = df[
    (df["MÊS"] == filtro_mes) &
    df['DIA'].isin(filtro_dia) &
    df['CULTO'].isin(filtro_culto) &
    df['CONGREGAÇÃO'].isin(filtro_cong)
]

# Tabela
st.subheader("📋 Programação Filtrada")
st.dataframe(df_filtrado)

# Gráfico de quantidade por tipo de culto
st.subheader("📊 Quantidade de cultos por tipo")
grafico = df_filtrado['CULTO'].value_counts()
st.bar_chart(grafico)

# Mapa com estilo Google
st.subheader("🗺️ Mapa das Congregações")
mapa_df = df_filtrado[['CONGREGAÇÃO', 'LAT', 'LON']].dropna()
if not mapa_df.empty:
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=mapa_df['LAT'].mean(),
            longitude=mapa_df['LON'].mean(),
            zoom=9,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=mapa_df,
                get_position='[LON, LAT]',
                get_radius=500,
                get_color=[0, 102, 255, 200],
                pickable=True,
            ),
        ],
        tooltip={"text": "{CONGREGAÇÃO}"}
    ))
else:
    st.warning("Nenhuma coordenada encontrada para exibir o mapa.")
