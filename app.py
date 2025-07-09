
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
from PIL import Image

st.set_page_config(page_title="Dashboard SDA", layout="wide")

# Barra superior fixa
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
</style>
<div class='fixed-header'><h2>BASE DE DADOS ESPACIAIS</h2></div>
""", unsafe_allow_html=True)

# Carregar dados
df = pd.read_excel("Produtores_SDA.xlsx")

# Coordenadas em float
df = df.dropna(subset=["COORDENADAS"])
df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.extract(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)').astype(float)

# GeoJSON dos distritos
with open("distrito.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# GeoJSON dos assentamentos
# GeoJSON das novas camadas
with open("Pocos.geojson", "r", encoding="utf-8") as f3:
    pocos_geojson = json.load(f3)

with open("Chafarizes.geojson", "r", encoding="utf-8") as f4:
    chafarizes_geojson = json.load(f4)

with open("Sistemas de Abastecimento.geojson", "r", encoding="utf-8") as f5:
    sistemas_geojson = json.load(f5)

with open("Assentamentos.geojson", "r", encoding="utf-8") as f2:
    assentamentos_geojson = json.load(f2)

# Sidebar - filtros
st.sidebar.title("🔎 Filtros")
if st.sidebar.button("🔄 Reiniciar Filtros"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))
produtor = st.sidebar.text_input("🔍 Buscar por nome do produtor")

# Filtragem
df_filtrado = df.copy()
if tecnicos:
    df_filtrado = df_filtrado[df_filtrado["TECNICO"].isin(tecnicos)]
if distritos:
    df_filtrado = df_filtrado[df_filtrado["DISTRITO"].isin(distritos)]
if compradores:
    df_filtrado = df_filtrado[df_filtrado["COMPRADOR"].isin(compradores)]
if produtor:
    df_filtrado = df_filtrado[df_filtrado["PRODUTOR"].str.contains(produtor, case=False, na=False)]

# Mapa
st.subheader("🗺️ Mapa com Distritos e Produtores")
if not df_filtrado.empty:
    center = [df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()]
    m = folium.Map(location=center, zoom_start=10, tiles="OpenStreetMap")

    # Ícone personalizado para Sistemas de Abastecimento
    custom_icon = folium.CustomIcon("./water-tank.png", icon_size=(30, 30))


    folium.GeoJson(geojson_data, name="Distritos").add_to(m)
    folium.GeoJson(assentamentos_geojson, name="Assentamentos", style_function=lambda x: {
        "color": "#800000",
        "weight": 2,
        "fillOpacity": 0.2
    }).add_to(m)

    for _, row in df_filtrado.iterrows():
        popup_info = (
            "<strong>Apelido:</strong> {}<br>"
            "<strong>Fazenda:</strong> {}<br>"
            "<strong>Distrito:</strong> {}<br>"
            "<strong>Escolaridade:</strong> {}<br>"
            "<strong>Contato:</strong> {}<br>"
            "<strong>RG:</strong> {}<br>"
            "<strong>CPF:</strong> {}<br>"
            "<strong>Data de Nascimento:</strong> {}<br>"
        ).format(
            row['APELIDO'], row['FAZENDA'], row['DISTRITO'], row['ESCOLARIDADE'],
            row['CONTATO'], row['RG'], row['CPF'], row['DATA NASCIMENTO']
        )

        folium.Marker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row["PRODUTOR"]
        ).add_to(m)

    
    folium.GeoJson(pocos_geojson, name="Poços", style_function=lambda x: {
        "color": "blue", "weight": 1, "fillOpacity": 0.4
    }).add_to(m)

    folium.GeoJson(chafarizes_geojson, name="Chafarizes", style_function=lambda x: {
        "color": "green", "weight": 1, "fillOpacity": 0.4
    }).add_to(m)

    
    for feature in sistemas_geojson['features']:
        coords = feature['geometry']['coordinates']
        # GeoJSON pode estar em ordem invertida (lon, lat)
        folium.Marker(
            location=[coords[1], coords[0]],
            icon=custom_icon,
            tooltip="Sistema de Abastecimento"
        ).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m)
else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")

# Tabela
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")
st.title("📋 Dados dos Produtores")
st.dataframe(df_filtrado[["TECNICO","PRODUTOR","APELIDO","FAZENDA","DISTRITO","ORDENHA?","INSEMINA?","LATICINIO","COMPRADOR"]], use_container_width=True)
