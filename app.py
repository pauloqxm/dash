
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json

st.set_page_config(page_title="Dashboard SDA - Folium", layout="wide")

# Estilos personalizados para a sidebar
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
        section[data-testid="stSidebar"] details:nth-of-type(2) summary {
            background-color: #0059b3 !important;
            color: white !important;
            font-weight: bold;
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

# GeoJSONs
with open("distrito.geojson", "r", encoding="utf-8") as f:
    geojson_distritos = json.load(f)
with open("Chafarizes.geojson", "r", encoding="utf-8") as f:
    geojson_chafarizes = json.load(f)
with open("Pocos.geojson", "r", encoding="utf-8") as f:
    geojson_pocos = json.load(f)
with open("Sistemas de Abastecimento.geojson", "r", encoding="utf-8") as f:
    geojson_sistemas = json.load(f)
with open("areas_reforma.geojson", "r", encoding="utf-8") as f:
    geojson_areas_reforma = json.load(f)
with open("distritos_ponto.geojson", "r", encoding="utf-8") as f:
    geojson_distritos_ponto = json.load(f)
with open("cisternas.geojson", "r", encoding="utf-8") as f:
    geojson_cisternas = json.load(f)
with open("acudes.geojson", "r", encoding="utf-8") as f:
    geojson_acudes = json.load(f)

# Sidebar
st.sidebar.title("🗺️ Controle de Camadas")

with st.sidebar.expander("🏘️ Infraestrutura"):
    show_distritos = st.checkbox("Distritos", value=True)
    show_distritos_ponto = st.checkbox("Sede Distritos", value=False)
    show_produtores = st.checkbox("Produtores", value=False)
    show_areas_reforma = st.checkbox("Áreas de Reforma", value=False)

with st.sidebar.expander("💧 Recursos Hídricos"):
    show_chafarizes = st.checkbox("Chafarizes", value=False)
    show_pocos = st.checkbox("Poços", value=False)
    show_cisternas = st.checkbox("Cisternas", value=False)
    show_sistemas = st.checkbox("Sistemas de Abastecimento", value=False)
    show_acudes = st.checkbox("Açudes", value=False)

st.sidebar.title("🔎 Filtros")

if st.sidebar.button("🔄 Reiniciar Filtros"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

tecnicos = st.sidebar.multiselect("👨‍🔧 Técnico", sorted(df["TECNICO"].dropna().unique()))
distritos = st.sidebar.multiselect("📍 Distrito", sorted(df["DISTRITO"].dropna().unique()))
compradores = st.sidebar.multiselect("🛒 Comprador", sorted(df["COMPRADOR"].dropna().unique()))
produtor = st.sidebar.text_input("🔍 Buscar Produtor")

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

total = len(df_filtrado)
st.success(f"{total} registro(s) encontrado(s).")
st.subheader("🗺️ Mapa com Distritos, Produtores e Áreas de Reforma")

if not df_filtrado.empty:
    center = [df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()]
    
    m = folium.Map(location=center, zoom_start=10, tiles=None)

    folium.TileLayer(
        tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.",
        name="Stamen Terrain"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.",
        name="Stamen Toner"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© OpenStreetMap contributors, © CARTO",
        name="CartoDB Positron"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="© OpenStreetMap contributors, © CARTO",
        name="CartoDB Dark Matter"
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, etc.",
        name="Esri Satellite"
    ).add_to(m)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)

    # Adicionar camadas de fundo com atribuições corretas  

    if show_distritos:
        folium.GeoJson(
            geojson_distritos,
            name="Distritos",
            style_function=lambda x: {'fillColor': '#9fe2fc', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
        ).add_to(m)

    if show_distritos_ponto:
        distritos_ponto_layer = folium.FeatureGroup(name="Sede Distritos")
        for feature in geojson_distritos_ponto["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Name: {Distrito}", max_width=200),
                icon=folium.CustomIcon("https://i.ibb.co/zwckDkW/gps.png", icon_size=(20, 20))
            ).add_to(distritos_ponto_layer)
        distritos_ponto_layer.add_to(m)

    if show_acudes:
        folium.GeoJson(
            geojson_acudes,
            name="Açudes",
            style_function=lambda x: {'fillColor': '#026ac4', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
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
                icon=folium.CustomIcon("https://i.ibb.co/My5kq3GH/icons8-fazenda-64.png", icon_size=(25, 25)),
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=row["PRODUTOR"]
          ).add_to(m)

    if show_areas_reforma:
        areas_layer = folium.FeatureGroup(name="Áreas de Reforma")
        for feature in geojson_areas_reforma["features"]:
            popup_text = feature["properties"].get("Name", "Sem Nome")
            folium.GeoJson(
                feature,
                name="Área de Reforma",
                tooltip=folium.GeoJsonTooltip(fields=["Name"], aliases=["Nome:"]),
                popup=folium.Popup(popup_text, max_width=300),
                style_function=lambda x: {"fillColor": "#ff7800", "color": "red", "weight": 1, "fillOpacity": 0.4}
            ).add_to(areas_layer)
        areas_layer.add_to(m)

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

    if show_pocos:
        pocos_layer = folium.FeatureGroup(name="Poços")
        for feature in geojson_pocos["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Poços",
                icon=folium.CustomIcon("https://i.ibb.co/mk8HRKv/chafariz.png", icon_size=(25, 15))
            ).add_to(pocos_layer)
        pocos_layer.add_to(m)

    if show_cisternas:
        cisternas_layer = folium.FeatureGroup(name="Cisternas")
        for feature in geojson_cisternas["features"]:
            coords = feature["geometry"]["coordinates"]
            Bairro_Loc = feature["properties"].get("Comunidade", "Sem nome")
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Comunidade: {Bairro_Loc}", max_width=200),
                tooltip="Cisternas",
                icon=folium.CustomIcon("https://i.ibb.co/Xkdpcnmx/water-tank.png", icon_size=(15, 15))
            ).add_to(cisternas_layer)
        cisternas_layer.add_to(m)

    if show_sistemas:
        sistemas_layer = folium.FeatureGroup(name="Sistemas de Abastecimento")
        for feature in geojson_sistemas["features"]:
            coords = feature["geometry"]["coordinates"]
            comunidade = feature["properties"].get("Comunidade", "Sem nome")
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Comunidade: {comunidade}", max_width=200),
                icon=folium.CustomIcon("https://i.ibb.co/jZh1WZyL/water-tower.png", icon_size=(25, 25))
            ).add_to(sistemas_layer)
        sistemas_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    folium_static(m, width=0, height=700)

else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")

# Tabela final
st.title("📋 Dados dos Produtores")
colunas = ["TECNICO", "PRODUTOR", "APELIDO", "FAZENDA", "DISTRITO", "ORDENHA?", "INSEMINA?", "LATICINIO", "COMPRADOR"]
st.dataframe(df_filtrado[colunas], use_container_width=True)
