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

try:
    # Carregar dados
    df = pd.read_excel("Produtores_SDA.xlsx")
    df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.split(",", expand=True)
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    df["ORDENHA?"] = df["ORDENHA?"].str.upper().fillna("NAO")
    df["INSEMINA?"] = df["INSEMINA?"].str.upper().fillna("NAO")

    # GeoJSONs
    geojson_files = {
        "distrito": "distrito.geojson",
        "chafarizes": "Chafarizes.geojson",
        "pocos": "pocos_profundos.geojson",
        "sistemas": "Sistemas de Abastecimento.geojson",
        "areas_reforma": "areas_reforma.geojson",
        "distritos_ponto": "distritos_ponto.geojson",
        "cisternas": "cisternas.geojson",
        "acudes": "acudes.geojson",
        "estradas": "estradas.geojson",
        "escolas": "escolas.geojson",
        "postos": "postos.geojson",
        "urbanas": "urbanas.geojson",
    }

    geojson_data = {}
    for name, file in geojson_files.items():
        try:
            with open(file, "r", encoding="utf-8") as f:
                geojson_data[name] = json.load(f)
        except FileNotFoundError:
            st.warning(f"Arquivo {file} não encontrado. A camada correspondente não será exibida.")
            geojson_data[name] = None
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.stop()

# Sidebar
st.sidebar.title("🗺️ Controle de Camadas")

with st.sidebar.expander("🏘️ Infraestrutura"):
    show_distritos = st.checkbox("Distritos", value=True)
    show_distritos_ponto = st.checkbox("Sede Distritos", value=False)
    show_produtores = st.checkbox("Produtores", value=False)
    show_areas_reforma = st.checkbox("Áreas de Reforma", value=False)
    show_estradas = st.checkbox("Estradas", value=False)
    show_escolas = st.checkbox("Escolas", value=False)
    show_postos = st.checkbox("Postos de Saúde", value=False)
    show_urbanas = st.checkbox("Áreas Urbanas", value=False)

with st.sidebar.expander("💧 Recursos Hídricos"):
    show_chafarizes = st.checkbox("Chafarizes", value=False)
    show_pocos = st.checkbox("Poços", value=False)
    show_cisternas = st.checkbox("Cisternas", value=False)
    show_sistemas = st.checkbox("Sistemas de Abastecimento", value=False)
    show_acudes = st.checkbox("Açudes", value=False)

st.sidebar.title("🔎 Filtros")

if st.sidebar.button("🔄 Reiniciar Filtros"):
    st.session_state.clear()
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
    # Calcular os limites do mapa com margem
    padding = 0.02  # graus de margem
    sw = [df_filtrado["LATITUDE"].min() - padding, df_filtrado["LONGITUDE"].min() - padding]
    ne = [df_filtrado["LATITUDE"].max() + padding, df_filtrado["LONGITUDE"].max() + padding]
    
    # Criar mapa centralizado na média
    m = folium.Map(
        location=[df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()],
        zoom_start=10,
        tiles=None
    )
    
    # Ajustar os limites do mapa para incluir todos os pontos
    m.fit_bounds([sw, ne])

    # Adicionar camadas de fundo
    tile_layers = [
        {
            "name": "Stamen Terrain",
            "url": "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
            "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
        },
        {
            "name": "Stamen Toner",
            "url": "https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
            "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
        },
        {
            "name": "CartoDB Positron",
            "url": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            "attr": "© OpenStreetMap contributors, © CARTO"
        },
        {
            "name": "CartoDB Dark Matter",
            "url": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            "attr": "© OpenStreetMap contributors, © CARTO"
        },
        {
            "name": "Esri Satellite",
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attr": "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, etc."
        },
        {
            "name": "OpenStreetMap",
            "url": "OpenStreetMap",
            "attr": ""
        }
    ]

    for layer in tile_layers:
        folium.TileLayer(
            tiles=layer["url"],
            attr=layer["attr"],
            name=layer["name"]
        ).add_to(m)

    # CAMADAS INFRAESTRUTURA
    
    if show_distritos and geojson_data.get("distrito"):
        folium.GeoJson(
            geojson_data["distrito"],
            name="Distritos",
            style_function=lambda x: {'fillColor': '#9fe2fc', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
        ).add_to(m)

    if show_distritos_ponto and geojson_data.get("distritos_ponto"):
        distritos_ponto_layer = folium.FeatureGroup(name="Sede Distritos")
        for feature in geojson_data["distritos_ponto"]["features"]:
            coords = feature["geometry"]["coordinates"]
            nome_distrito = feature["properties"].get("Name", "Sem nome")
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Distrito: {nome_distrito}", max_width=200),
                icon=folium.CustomIcon("https://i.ibb.co/zwckDkW/gps.png", icon_size=(20, 20))
            ).add_to(distritos_ponto_layer)
        distritos_ponto_layer.add_to(m)
        
    if show_estradas and geojson_data.get("estradas"):
        folium.GeoJson(
            geojson_data["estradas"],
            name="estradas",
            style_function=lambda x: {'fillColor': '#802f04', 'fillOpacity': 0.2, 'color': '#802f04', 'weight': 1}
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
                icon=folium.CustomIcon("https://i.ibb.co/zVBVzh2t/fazenda.png", icon_size=(20, 20)),
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=row["PRODUTOR"]
            ).add_to(m)

    if show_areas_reforma and geojson_data.get("areas_reforma"):
        areas_layer = folium.FeatureGroup(name="Áreas de Reforma")
        for feature in geojson_data["areas_reforma"]["features"]:
            popup_text = feature["properties"].get("Name", "Sem Nome")
            folium.GeoJson(
                feature,
                name="Área de Reforma",
                tooltip=folium.GeoJsonTooltip(fields=["Name"], aliases=["Nome:"]),
                popup=folium.Popup(popup_text, max_width=300),
                style_function=lambda x: {"fillColor": "#ff7800", "color": "red", "weight": 1, "fillOpacity": 0.4}
            ).add_to(areas_layer)
        areas_layer.add_to(m)
        
    if show_escolas and geojson_data.get("escolas"):
        escolas_layer = folium.FeatureGroup(name="Escolas")
        for feature in geojson_data["escolas"]["features"]:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]
            popup_info = (
    "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
    "<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B; border-bottom: 1px solid #ccc;'>🏫 Escola Municipal</h4>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📛 Nome:</span> " + props.get("no_entidad", "Sem nome") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📍 Endereço:</span> " + props.get("endereco", "Não informado") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📞 Contato:</span> " + str(props.get("fone_1", "Não informado")) + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>🧭 Localização:</span> " + props.get("no_localiz", "Não informado") + "</p>"
    "</div>"

            )
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=props.get("no_entidad", "Sem nome"),
                icon=folium.CustomIcon(
                    "https://i.ibb.co/pBsQcQws/education.png",
                    icon_size=(25, 25)
                )
            ).add_to(escolas_layer)
        escolas_layer.add_to(m)

    if show_postos and geojson_data.get("postos"):
        postos_layer = folium.FeatureGroup(name="Postos")
        for feature in geojson_data["postos"]["features"]:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]
            popup_info = (
    "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
    "<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B; border-bottom: 1px solid #ccc;'>🏥 Postos de Saúde</h4>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📛 Posto:</span> " + props.get("nome", "Sem nome") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📍 Endereço:</span> " + props.get("endereco", "Não informado") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📞 Bairro:</span> " + str(props.get("bairro", "Não informado")) + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>🧭 Município:</span> " + props.get("municipio", "Não informado") + "</p>"
    "</div>"

            )
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=props.get("nome", "Sem nome"),
                icon=folium.CustomIcon(
                    "https://i.ibb.co/rGdw6d71/hospital.png",
                    icon_size=(25, 25)
                )
            ).add_to(postos_layer)
        postos_layer.add_to(m)

    if show_urbanas and geojson_data.get("urbanas"):
        folium.GeoJson(
            geojson_data["urbanas"],
            name="Aréas Urbanas",
            style_function=lambda x: {'fillColor': '#9e064d', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
        ).add_to(m)


    # CAMADAS RECURSOS HÍDRICOS

    if show_chafarizes and geojson_data.get("chafarizes"):
        chafarizes_layer = folium.FeatureGroup(name="Chafarizes")
        for feature in geojson_data["chafarizes"]["features"]:
            coords = feature["geometry"]["coordinates"]
            folium.Marker(
                location=[coords[1], coords[0]],
                tooltip="Chafariz",
                icon=folium.CustomIcon("https://i.ibb.co/mk8HRKv/chafariz.png", icon_size=(25, 15))
            ).add_to(chafarizes_layer)
        chafarizes_layer.add_to(m)

    if show_pocos and geojson_data.get("pocos"):
        pocos_layer = folium.FeatureGroup(name="Poços")
        for feature in geojson_data["pocos"]["features"]:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]
            popup_info = (
    "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
    "<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B; border-bottom: 1px solid #ccc;'>🏫 Escola Municipal</h4>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📛 Comunidade:</span> " + props.get("Localidade", "Sem nome") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📍 Profunidade:</span> " + props.get("Profundida", "Não informado") + "</p>"
    "<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>🧭 Vazão:</span> " + props.get("Vazão_LH_2", "Não informado") + "</p>"
    "</div>"

            )
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=props.get("no_entidad", "Sem nome"),
                icon=folium.CustomIcon(
                    "https://i.ibb.co/6JrpxXMT/water.png",
                    icon_size=(25, 25)
                )
            ).add_to(pocos_layer)
        pocos_layer.add_to(m)

    if show_cisternas and geojson_data.get("cisternas"):
        cisternas_layer = folium.FeatureGroup(name="Cisternas")
        for feature in geojson_data["cisternas"]["features"]:
            coords = feature["geometry"]["coordinates"]
            Bairro_Loc = feature["properties"].get("Comunidade", "Sem nome")
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(f"Comunidade: {Bairro_Loc}", max_width=200),
                tooltip="Cisternas",
                icon=folium.CustomIcon("https://i.ibb.co/jvLz192m/water-tank.png", icon_size=(18, 18))
            ).add_to(cisternas_layer)
        cisternas_layer.add_to(m)

    if show_acudes and geojson_data.get("acudes"):
        folium.GeoJson(
            geojson_data["acudes"],
            name="Açudes",
            style_function=lambda x: {'fillColor': '#026ac4', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
        ).add_to(m)

    
    if show_sistemas and geojson_data.get("sistemas"):
        sistemas_layer = folium.FeatureGroup(name="Sistemas de Abastecimento")
        for feature in geojson_data["sistemas"]["features"]:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]
            popup_info = (
                "<strong>Comunidade:</strong> " + props.get("Comunidade", "Sem nome") + "<br>"
                "<strong>Associação:</strong> " + props.get("Associacao", "Não informado") + "<br>"
                "<strong>Ano:</strong> " + str(props.get("Ano", "Não informado")) + "<br>"
                "<strong>Município:</strong> " + props.get("Municipio", "Não informado")
            )
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=props.get("Comunidade", "Sem nome"),
                icon=folium.CustomIcon(
                    "https://i.ibb.co/sd8DxJQ5/water-tower.png",
                    icon_size=(25, 25)
                )
            ).add_to(sistemas_layer)
        sistemas_layer.add_to(m) 
    
    folium.LayerControl(collapsed=True).add_to(m)
    folium_static(m, width=1200, height=700)

else:
    st.info("Nenhum produtor encontrado com os filtros selecionados.")

# Tabela final
st.title("📋 Dados dos Produtores")
colunas = ["TECNICO", "PRODUTOR", "APELIDO", "FAZENDA", "DISTRITO", "ORDENHA?", "INSEMINA?", "LATICINIO", "COMPRADOR"]
st.dataframe(df_filtrado[colunas], use_container_width=True)
