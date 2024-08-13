import plotly.express as px
import pandas as pd
import json

def load_geojson(file_path):
    """Load GeoJSON data from a file."""
    try:
        with open(file_path) as f:
            geojson_data = json.load(f)
        print('GeoJSON data loaded successfully.')
        return geojson_data
    except Exception as e:
        print(f"Error loading GeoJSON data: {e}")
        return None

def load_csv(file_path):
    """Load CSV data into a DataFrame."""
    try:
        df = pd.read_csv(file_path)
        print('CSV data loaded successfully.')
        return df
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return None

def create_scatter_map(df):
    """Create a scatter mapbox plot for tire shops."""
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
            "LONGITUDE": False,
            "LATITUDE": False,
            "STORE_NAME": True,
            "ADDRESS": True,
            "ZIP": True,
            "POTENTIAL_MARKET": True,
            "AVERAGE_INCOME": True
        }
    )
    return fig

def add_choropleth(fig, df, geojson_data):
    """Add a choropleth layer to the mapbox plot."""
    fig.add_trace(
        px.choropleth_mapbox(
            geojson=geojson_data,
            locations=df['ZIP'],
            featureidkey="properties.ZIP_CODE",
            color=df['ZIP'],
            color_continuous_scale="Viridis",
            mapbox_style="open-street-map"
        ).data[0]
    )
    return fig

def update_hover_data(fig, df):
    """Update hover data for the mapbox plot."""
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>"
                      "<b>ZIP Code: %{location}</b><br>"
                      "Store Name: %{customdata[0]}<br>"
                      "Address: %{customdata[1]}<br>"
                      "Max Potential Market: %{customdata[2]}<br>"
                      "Avg Area Revenue: %{customdata[3]}<br>",
        customdata=df[["STORE_NAME", "ADDRESS", "POTENTIAL_MARKET", "AVERAGE_INCOME"]].values 
    )
    return fig

def main():
    # Load GeoJSON and CSV data
    zip_code_geojson = load_geojson('zip_bounds.geojson')
    df = load_csv("illinois_results.csv")
    
    if zip_code_geojson is None or df is None:
        print("Data loading failed. Exiting.")
        return

    # Create scatter mapbox plot
    fig = create_scatter_map(df)

    # Add choropleth layer
    fig = add_choropleth(fig, df, zip_code_geojson)

    # Update hover data
    fig = update_hover_data(fig, df)

    # Update layout and show plot
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0, "t":50, "l":0, "b":10})
    
    print('Generating plot...')
    fig.show()
    print('Plot generation complete.')

if __name__ == "__main__":
    main()
