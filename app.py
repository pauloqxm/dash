
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json

st.set_page_config(page_title="Dashboard SDA - Folium", layout="wide")

# Barra fixa no topo
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)


# Carregar dados
df = pd.read_excel("Produtores_SDA.xlsx")
df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.split(",", expand=True)
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
df["ORDENHA?"] = df["ORDENHA?"].str.upper().fillna("NAO")
df["INSEMINA?"] = df["INSEMINA?"].str.upper().fillna("NAO")

# Carregar GeoJSON
with open("distrito.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Filtros
st.sidebar.title("🔎 Filtros")
tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))
produtor = st.sidebar.text_input("🔍 Buscar Produtor")

# Estilo do mapa
tile_option = st.sidebar.selectbox("🗺️ Estilo do Mapa", [
    "OpenStreetMap",
    "Stamen Terrain",
    "Stamen Toner",
    "CartoDB positron",
    "CartoDB dark_matter",
    "Esri Satellite"
])

tile_urls = {
    "Esri Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
}

tile_attr = {
    "Esri Satellite": "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, etc."
}

# Aplicar filtros
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
    if tile_option in tile_urls:
        m = folium.Map(location=center, zoom_start=10, tiles=None)
        folium.TileLayer(tiles=tile_urls[tile_option], attr=tile_attr[tile_option], name=tile_option).add_to(m)
    else:
        m = folium.Map(location=center, zoom_start=10, tiles=tile_option)

    folium.GeoJson(geojson_data, name="Distritos").add_to(m)

    for _, row in df_filtrado.iterrows():
        popup_info = f"""
        <strong>Apelido:</strong> {row['APELIDO']}<br>
        <strong>Fazenda:</strong> {row['FAZENDA']}<br>
        <strong>Distrito:</strong> {row['DISTRITO']}<br>
        <strong>Escolaridade:</strong> {row['ESCOLARIDADE']}<br>
        <strong>Contato:</strong> {row['CONTATO']}<br>
        <strong>RG:</strong> {row['RG']}<br>
        <strong>CPF:</strong> {row['CPF']}<br>
        <strong>Data de Nascimento:</strong> {row['DATA NASCIMENTO']}<br>
        """
        folium.Marker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row["PRODUTOR"]
        ).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m)
else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")

# Tabela (após o mapa)
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")
st.title("📋 Dados dos Produtores")
st.dataframe(df_filtrado, use_container_width=True)

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
st.subheader("🗺️ Mapa com Distritos e Produtores")

if not df_filtrado.empty:
    center = [df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()]
    if tile_option in tile_urls:
        m = folium.Map(location=center, zoom_start=10, tiles=None)
        folium.TileLayer(tiles=tile_urls[tile_option], attr=tile_attr[tile_option], name=tile_option).add_to(m)
    else:
        m = folium.Map(location=center, zoom_start=10, tiles=tile_option)

    folium.GeoJson(geojson_data, name="Distritos").add_to(m)

    for _, row in df_filtrado.iterrows():
        popup_info = f"""
        <strong>Apelido:</strong> {row['APELIDO']}<br>
        <strong>Fazenda:</strong> {row['FAZENDA']}<br>
        <strong>Distrito:</strong> {row['DISTRITO']}<br>
        <strong>Escolaridade:</strong> {row['ESCOLARIDADE']}<br>
        <strong>Contato:</strong> {row['CONTATO']}<br>
        <strong>RG:</strong> {row['RG']}<br>
        <strong>CPF:</strong> {row['CPF']}<br>
        <strong>Data de Nascimento:</strong> {row['DATA NASCIMENTO']}<br>
        """
        folium.Marker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row["PRODUTOR"]
        ).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m)
else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")
