
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="📖 Programação ADTC", layout="wide")
st.title("📖 Programação de Cultos - ADTC")

# Carregar dados
df = pd.read_excel("ADTC_PROGRAMAÇÃO.xlsx")
df.columns = [col.strip().upper() for col in df.columns]

# Separar latitude e longitude
df[['LAT', 'LON']] = df['COORDENADAS'].str.split(',', expand=True)
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')

# Filtros
dias = df['DIA'].unique().tolist()
cultos = df['CULTO'].unique().tolist()
congs = df['CONGREGAÇÃO'].unique().tolist()

st.sidebar.header("Filtros")
filtro_dia = st.sidebar.multiselect("Dia da semana", dias, default=dias)
filtro_culto = st.sidebar.multiselect("Tipo de culto", cultos, default=cultos)
filtro_cong = st.sidebar.multiselect("Congregação", congs, default=congs)

# Aplicar filtros
df_filtrado = df[
    df['DIA'].isin(filtro_dia) &
    df['CULTO'].isin(filtro_culto) &
    df['CONGREGAÇÃO'].isin(filtro_cong)
]

# Exibir tabela
st.subheader("📋 Programação Filtrada")
st.dataframe(df_filtrado)

# Gráfico de quantidade por tipo de culto
st.subheader("📊 Quantidade de cultos por tipo")
grafico = df_filtrado['CULTO'].value_counts()
st.bar_chart(grafico)

# Mapa com coordenadas
st.subheader("🗺️ Mapa das Congregações")
mapa_df = df_filtrado[['CONGREGAÇÃO', 'LAT', 'LON']].dropna()
if not mapa_df.empty:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
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
                get_color=[200, 30, 0, 160],
                pickable=True,
            ),
        ],
        tooltip={"text": "{CONGREGAÇÃO}"}
    ))
else:
    st.warning("Nenhuma coordenada encontrada para exibir o mapa.")
