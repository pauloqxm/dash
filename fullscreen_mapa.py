
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MeasureControl, Draw, MousePosition
import json
import pandas as pd

st.set_page_config(layout="wide")

# Carrega dados básicos
df = pd.read_excel("Produtores_SDA.xlsx")
df[["LATITUDE", "LONGITUDE"]] = df["COORDENADAS"].str.split(",", expand=True)
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

with open("distrito.geojson", "r", encoding="utf-8") as f:
    distritos = json.load(f)

m = folium.Map(location=[-5.1971, -39.2886], zoom_start=10, tiles="OpenStreetMap")
m.add_child(MeasureControl(primary_length_unit="meters", primary_area_unit="hectares"))
MousePosition().add_to(m)
Draw(export=True).add_to(m)

folium.GeoJson(
    distritos,
    name="Distritos",
    style_function=lambda x: {'fillColor': '#9fe2fc', 'fillOpacity': 0.2, 'color': '#000000', 'weight': 1}
).add_to(m)

for _, row in df.iterrows():
    folium.Marker(
        location=[row["LATITUDE"], row["LONGITUDE"]],
        tooltip=row["PRODUTOR"],
        icon=folium.Icon(color='blue', icon='user')
    ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
folium_static(m, width=0, height=0)
