import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json

st.set_page_config(page_title="Dashboard SDA - Folium", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        .fixed-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #004080;
            color: white;
            text-align: center;
            padding: 10px 0;
            z-index: 9999;
        }
        .reportview-container .main {
            padding-top: 70px;
        }

        section[data-testid="stSidebar"] details:nth-of-type(1) summary {
            background-color: #003366 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
        }
        section[data-testid="stSidebar"] details:nth-of-type(1)[open] {
            background-color: #003366 !important;
            border-radius: 5px;
        }
        section[data-testid="stSidebar"] details:nth-of-type(1)[open] > div {
            background-color: #e6f0ff !important;
            padding: 10px;
            border-radius: 5px;
        }

        section[data-testid="stSidebar"] details:nth-of-type(2) summary {
            background-color: #0059b3 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
        }
        section[data-testid="stSidebar"] details:nth-of-type(2)[open] {
            background-color: #0059b3 !important;
            border-radius: 5px;
        }
        section[data-testid="stSidebar"] details:nth-of-type(2)[open] > div {
            background-color: #e0ecff !important;
            padding: 10px;
            border-radius: 5px;
        }

        section[data-testid="stSidebar"] div:nth-of-type(4) > div {
            background-color: #d9e9ff !important;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    <div class='fixed-header'><h2>BASE DE DADOS ESPACIAIS</h2></div>
""", unsafe_allow_html=True)

# Carregar dados
df = pd.read_excel("Produtores_SDA.xlsx")
df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.split(",", expand=True)
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
df["ORDENHA?"] = df["ORDENHA?"].str.upper().fillna("NAO")
df["INSEMINA?"] = df["INSEMINA?"].str.upper().fillna("NAO")

# Carregar GeoJSONs
with open("distrito.geojson", "r", encoding="utf-8") as f:
    geojson_distrito = json.load(f)
with open("Chafarizes.geojson", "r", encoding="utf-8") as f:
    geojson_chafarizes = json.load(f)

# SIDEBAR
st.sidebar.title("🗺️ Controle de Camadas")
with st.sidebar.expander("🏘️ Infraestrutura"):
    show_distritos = st.checkbox("Distritos", value=True)
with st.sidebar.expander("💧 Recursos Hídricos"):
    show_chafarizes = st.checkbox("Chafarizes", value=False)
st.sidebar.title("🔎 Filtros")
produtor = st.sidebar.text_input("🔍 Buscar Produtor")

# Aplicar filtro
df_filtrado = df.copy()
if produtor:
    df_filtrado = df_filtrado[df_filtrado["PRODUTOR"].str.contains(produtor, case=False, na=False)]

# Mapa
if not df_filtrado.empty:
    center = [df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()]
    m = folium.Map(location=center, zoom_start=10)

    if show_distritos:
        folium.GeoJson(
            geojson_distrito,
            name="Distritos",
            style_function=lambda x: {'fillColor': '#9fe2fc', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
        ).add_to(m)

    if show_chafarizes:
        chafarizes_layer = folium.FeatureGroup(name="Chafarizes")
        for feature in geojson_chafarizes["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Chafariz",
                icon=folium.Icon(color="blue", icon="tint", prefix="fa")
            ).add_to(chafarizes_layer)
        chafarizes_layer.add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m, width=0, height=700)
else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")

# Tabela final
st.title("\U0001F4CB Dados dos Produtores")
colunas = ["TECNICO", "PRODUTOR", "APELIDO", "FAZENDA", "DISTRITO", "ORDENHA?", "INSEMINA?"]
st.dataframe(df_filtrado[colunas], use_container_width=True)
