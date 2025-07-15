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

with open("Chafarizes.geojson") as f:
    chafarizes_geojson = json.load(f)
with open("Pocos.geojson") as f:
    pocos_geojson = json.load(f)
with open("Sistemas de Abastecimento.geojson") as f:
    sistemas_geojson = json.load(f)
with open("Assentamentos.geojson") as f:
with open("areas_reforma.geojson") as f:
    areas_reforma_geojson = json.load(f)
    assentamentos_geojson = json.load(f)

# SIDEBAR - CONTROLE DE CAMADAS (AGORA VEM PRIMEIRO)
st.sidebar.title("🗺️ Controle de Camadas")

with st.sidebar.expander("🏘️ Infraestrutura"):
    show_distritos = st.checkbox("Distritos", value=True)
    show_produtores = st.checkbox("Produtores", value=True)
    show_assentamentos = st.checkbox("Assentamentos", value=False)

show_areas_reforma = st.checkbox("Áreas de Reforma", value=False)
    with st.sidebar.expander("💧 Recursos Hídricos"):
    show_chafarizes = st.checkbox("Chafarizes", value=False)
    show_pocos = st.checkbox("Poços", value=False)
    show_sistemas = st.checkbox("Sistemas de Abastecimento", value=False)

# SIDEBAR - FILTROS (AGORA VEM DEPOIS)
st.sidebar.title("🔎 Filtros")

# Botão para reiniciar filtros usando session_state
if st.sidebar.button("🔄 Reiniciar Filtros"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

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

# Resto do código permanece igual...
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

# Tabela
st.success(f"{len(df_filtrado)} registro(s) encontrado(s).")
st.subheader("🗺️ Mapa com Distritos e Produtores")

if not df_filtrado.empty:
    center = [df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()]
    if tile_option in tile_urls:
        m = folium.Map(location=center, zoom_start=10, tiles=None)
        folium.TileLayer(tiles=tile_urls[tile_option], attr=tile_attr[tile_option], name=tile_option).add_to(m)
    else:
        m = folium.Map(location=center, zoom_start=10, tiles=tile_option)

    # Adicionar camadas conforme seleção
    if show_distritos:
        folium.GeoJson(
            geojson_data, 
            name="Distritos",
            style_function=lambda x: {'fillColor': '#ffff00', 'color': '#000000', 'weight': 1}
        ).add_to(m)

    if show_produtores:
        for _, row in df_filtrado.iterrows():
            popup_info = f"""
            <strong>Apelido:</strong> {row['APELIDO']}<br>
            <strong>Produção dia:</strong> {row['PRODUCAO']}<br>
            <strong>Fazenda:</strong> {row['FAZENDA']}<br>
            <strong>Distrito:</strong> {row['DISTRITO']}<br>
            <strong>Escolaridade:</strong> {row['ESCOLARIDADE']}<br>
            """
            folium.Marker(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                icon=folium.Icon(color="blue", icon="info-sign"),
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=row["PRODUTOR"]
            ).add_to(m)

    if show_chafarizes:
        chafarizes_layer = folium.FeatureGroup(name="Chafarizes")
        for feature in chafarizes_geojson["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Chafariz",
                icon=folium.Icon(color="blue", icon="tint", prefix="fa")
            ).add_to(chafarizes_layer)
        chafarizes_layer.add_to(m)

    if show_pocos:
        pocos_layer = folium.FeatureGroup(name="Poços")
        for feature in pocos_geojson["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Poço",
                icon=folium.Icon(color="green", icon="water", prefix="fa")
            ).add_to(pocos_layer)
        pocos_layer.add_to(m)

    if show_sistemas:
        sistemas_layer = folium.FeatureGroup(name="Sistemas de Abastecimento")
        for feature in sistemas_geojson["features"]:
            coords = feature["geometry"]["coordinates"]
            comunidade = feature["properties"].get("Comunidade", "Sem nome")
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Comunidade: {comunidade}", max_width=200),
                icon=folium.CustomIcon("water-tank.png", icon_size=(30, 30))
            ).add_to(sistemas_layer)
        sistemas_layer.add_to(m)

    if show_assentamentos:
    if show_areas_reforma:
        areas_layer = folium.FeatureGroup(name="Áreas de Reforma")
        folium.GeoJson(
            areas_reforma_geojson,
            name="Áreas de Reforma",
            tooltip=folium.GeoJsonTooltip(fields=["Nome", "Código"], aliases=["Nome:", "Código:"]),
            style_function=lambda x: {"fillColor": "#ff7800", "color": "black", "weight": 1, "fillOpacity": 0.4}
        ).add_to(areas_layer)
        areas_layer.add_to(m)

        assentamentos_layer = folium.FeatureGroup(name="Assentamentos")
        for feature in assentamentos_geojson["features"]:
            if feature["geometry"]["type"] != "Point":
                continue
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Assentamento",
                icon=folium.Icon(color="purple", icon="home", prefix="fa")
            ).add_to(assentamentos_layer)
        assentamentos_layer.add_to(m)

    # Manter o LayerControl para quem prefere controlar diretamente no mapa
    folium.LayerControl().add_to(m)
    folium_static(m, width=0, height=700)
else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")
st.title("📋 Dados dos Produtores")
st.dataframe(df_filtrado[["TECNICO","PRODUTOR","APELIDO","FAZENDA","DISTRITO","ORDENHA?","INSEMINA?","LATICINIO","COMPRADOR"]], use_container_width=True)

# Mapa
