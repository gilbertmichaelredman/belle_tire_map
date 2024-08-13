import streamlit as st
import re
import plotly.express as px
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def extract_zip(address):
    # Regular expression to match a 5-digit ZIP code (with optional 4-digit extension)
    match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
    if match:
        return match.group(0)
    return None


# Streamlit UI components
st.title("Belle Tire Chicago DMA with Local Competitors")

st.write("This app visualizes Belle Tire locations and nearby competitors within different radius distances.")



# Load  data
@st.cache_data
def load_data():
    df_belle_tire = pd.read_csv("illinois_results.csv")
    df_competitors = pd.read_csv("competitors.csv")
    df_competitors['ZIP'] = df_competitors['ADDRESS'].apply(extract_zip)
    return df_belle_tire, df_competitors

df_belle_tire, df_competitors = load_data()

# Convert Belle Tire and Competitor data to GeoDataFrames
gdf_belle_tire = gpd.GeoDataFrame(
    df_belle_tire, 
    geometry=[Point(xy) for xy in zip(df_belle_tire['LONGITUDE'], df_belle_tire['LATITUDE'])],
    crs="EPSG:4326"  # WGS84 Latitude/Longitude
)

gdf_competitors = gpd.GeoDataFrame(
    df_competitors, 
    geometry=[Point(xy) for xy in zip(df_competitors['LONGITUDE'], df_competitors['LATITUDE'])],
    crs="EPSG:4326"  # WGS84 Latitude/Longitude
)

# Reproject to a coordinate system that uses meters (UTM zone 16N, EPSG:32616)
gdf_belle_tire = gdf_belle_tire.to_crs(epsg=32616)
gdf_competitors = gdf_competitors.to_crs(epsg=32616)

#count competitors within a radius (e.g., 5 miles)
def count_nearby_competitors(belle_tire_row, competitors_gdf, radius):
    buffer = belle_tire_row.geometry.buffer(radius*1609.34)  # Radius in degrees (approximation for miles)
    competitors_within_radius = competitors_gdf[competitors_gdf.geometry.within(buffer)]
    return len(competitors_within_radius)

#calculate the number of competitors near each Belle Tire store
gdf_belle_tire['competitors_within_5'] = gdf_belle_tire.apply(count_nearby_competitors, competitors_gdf=gdf_competitors, radius=5, axis=1)
gdf_belle_tire['competitors_within_7'] = gdf_belle_tire.apply(count_nearby_competitors, competitors_gdf=gdf_competitors, radius=7, axis=1)
gdf_belle_tire['competitors_within_10'] = gdf_belle_tire.apply(count_nearby_competitors, competitors_gdf=gdf_competitors, radius=10, axis=1)

# Reproject back to WGS84 for plotting
gdf_belle_tire = gdf_belle_tire.to_crs(epsg=4326)
gdf_competitors = gdf_competitors.to_crs(epsg=4326)

# plot belle tire
fig = px.scatter_mapbox(
    gdf_belle_tire,
    lon=gdf_belle_tire.geometry.x,  
    lat=gdf_belle_tire.geometry.y,   
    zoom=8,
    width=1400,
    height=1000,
    title="Belle Tire Chicago DMA w/ local competitors",
    hover_name="CITY",
    hover_data={
        "LONGITUDE":False,
        "LATITUDE": False,
        "STORE_NAME": True,
        "ADDRESS": True,
        "ZIP": True,
        "POTENTIAL_MARKET": False,
        "AVERAGE_INCOME": True,
        "competitors_within_5": True,
        "competitors_within_7": True,
        "competitors_within_10": True
    },
    color_discrete_sequence=["#1f77b4"],
    size_max=40
)

# Customize hover information for Belle Tire stores
fig.update_traces(
     hovertemplate="<b>%{hovertext}</b><br>" +
                  "Store Name: %{customdata[0]}<br>" +
                  "Address: %{customdata[1]}<br>" +
                  "ZIP: %{customdata[2]}<br>" +
                  "Avg Income: %{customdata[7]}<br>"
                  "Competitors within 5 miles: %{customdata[3]}<br>" +
                  "Competitors within 7 miles: %{customdata[4]}<br>" +
                  "Competitors within 10 miles: %{customdata[5]}<br>",
    customdata=gdf_belle_tire[["STORE_NAME", "ADDRESS", "ZIP", "competitors_within_5", "competitors_within_7", "competitors_within_10", "POTENTIAL_MARKET", "AVERAGE_INCOME"]].values,
    marker=dict(size=15, opacity=0.9),  # Ensure larger size for Belle Tire stores
    selector=dict(marker=dict(color="#1f77b4"))  # Apply only to Belle Tire stores
  )


# Plot Competitor stores on the same map
fig.add_trace(
    px.scatter_mapbox(
        gdf_competitors,
        lon=gdf_competitors.geometry.x,  
        lat=gdf_competitors.geometry.y,   
        hover_name="COMPETITOR_NAME",
        hover_data={
            "LONGITUDE":False,
            "LATITUDE": False,
            "ADDRESS": True,
            "ZIP": True
        },
        color_discrete_sequence=["#ff7f0e"],  # Red for Competitor stores
        size_max=6  # Adjust the size of the markers
    ).update_traces(
        marker=dict(size=10, opacity=0.8),
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Address: %{customdata[0]}<br>" +
                      "ZIP: %{customdata[1]}<br>",
        customdata=gdf_competitors[["ADDRESS", "ZIP"]].values
    ).data[0]
)

# Update layout
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":50,"l":0,"b":10},
    title=dict(
        text="Belle Tire Chicago DMA with Local Competitors",
        font=dict(size=24, family="Arial", color="Black"),
        x=0.5,
        xanchor='center'
    ),
    legend=dict(
        title="Legend",
        x=0.01,
        y=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1
    )
)


#display in streamlit
st.plotly_chart(fig)