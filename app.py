
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="📖 Programação ADTC", layout="wide")
st.title("📖 Programação de Cultos - ADTC")

# Carregar dados
try:
    df = pd.read_excel("ADTC_PROGRAMAÇÃO.xlsx")
except Exception as e:
    st.error("Erro ao carregar a planilha: " + str(e))
    st.stop()

df.columns = [col.strip().upper() for col in df.columns]

# Tratar colunas de dia
dias_map = {
    "Domingo": 7, "Segunda-Feira": 1, "Terça-Feira": 2,
    "Quarta-Feira": 3, "Quinta-Feira": 4, "Sexta-Feira": 5, "Sábado": 6
}
df["DIA_NUM"] = df["DIA"].map(dias_map)
df["DATA_FICTICIA"] = pd.to_datetime("2025-07-01") + pd.to_timedelta(df["DIA_NUM"].fillna(1) - 1, unit='d')

nomes_meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
df["MÊS"] = df["DATA_FICTICIA"].dt.month.map(nomes_meses)

# Coordenadas seguras
if "COORDENADAS" in df.columns:
    try:
        df[['LAT', 'LON']] = df['COORDENADAS'].str.split(',', expand=True)
        df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
        df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
    except Exception as e:
        st.warning("Erro ao processar coordenadas: " + str(e))
        df["LAT"], df["LON"] = None, None
else:
    df["LAT"], df["LON"] = None, None

# Filtros disponíveis
meses = df["MÊS"].dropna().unique().tolist()
dias = df['DIA'].dropna().unique().tolist()
cultos = df['CULTO'].dropna().unique().tolist()
congs = df['CONGREGAÇÃO'].dropna().unique().tolist()

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
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    st.dataframe(df_filtrado)

    # Gráfico
    st.subheader("📊 Quantidade de cultos por tipo")
    grafico = df_filtrado['CULTO'].value_counts()
    st.bar_chart(grafico)

    # Mapa
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
        st.info("Nenhuma coordenada válida para exibir no mapa.")
