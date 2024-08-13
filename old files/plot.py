import plotly.express as px
import pandas as pd
import json

print('getting zip data')

#Load data from GeoJSON zip code boundaries

#with open('zip_bounds.geojson') as f:
#    zip_code_geojson = json.load(f)#
print('zip data loaded')

print('getting belle_tire data')
# Load data from the CSV file
df = pd.read_csv("illinois_results.csv")
print('belle_tire loaded')

# Verify column names
print("Columns in the DataFrame:", df.columns)

# Create scatter mapbox plot
fig = px.scatter_mapbox(
    df,
    lon="LONGITUDE",  
    lat="LATITUDE",   
    zoom=8,
    width=1200,
    height=900,
    title="Tire Shops",
    hover_name="CITY",
    hover_data={
        "LONGITUDE":False,
        "LATITUDE": False,
        "STORE_NAME": True,
        "ADDRESS": True,
        "ZIP": True,
        "POTENTIAL_MARKET": True,
        "AVERAGE_INCOME": True

    }
)

print('mapping zip codes')

fig.add_trace(
    px.choropleth_mapbox(
        geojson=zip_code_geojson,
        locations=df['ZIP'],
        featureidkey="PROPERTIES.ZIP_CODE",
        color=df['ZIP'],
        color_continuous_scale="Viridis",
        mapbox_style="open-street-map"
    ).data[0]
)

print('mapping hover data')
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>"
                  "<b>ZIP Code: %{location}</b><br>"
                  #"Store Name: %{customdata[0]:,}<br>"  #STORE_NAME showing as NaN, not sure why
                  "Address: %{customdata[1]}<br>"
                  "Max Potential Market: %{customdata[2]}<br>"
                  "Avg Area Revenue: %{customdata[3]}<br>",
    customdata=df[["STORE_NAME", "ADDRESS", "ZIP","POTENTIAL_MARKET","AVERAGE_INCOME"]].values 


)

# Update layout
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":10})

print('generating plot')
# Show plot
fig.show()

print('done')