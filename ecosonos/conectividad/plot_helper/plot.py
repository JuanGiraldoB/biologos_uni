import pandas as pd
import numpy as np
import random
from shapely.geometry import Polygon, Point
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import json
import plotly.express as px


def create_map(df_points):
    fig = go.Figure(go.Choroplethmapbox(
        # geojson=departamentos,
        # locations=locs,
        # z=df['departamento'],
        colorscale='Viridis',
        colorbar_title="id",
        showlegend=False,
        showscale=False
    ))

    buffer_degrees = 0.02

    min_lat = df_points['latitude_IG'].min()
    max_lat = df_points['latitude_IG'].max()
    min_lon = df_points['longitud_IG'].min()
    max_lon = df_points['longitud_IG'].max()

    lons_box = [min_lon - buffer_degrees, min_lon - buffer_degrees,
                max_lon + buffer_degrees, max_lon + buffer_degrees,
                min_lon - buffer_degrees]

    lats_box = [min_lat - buffer_degrees, max_lat + buffer_degrees,
                max_lat + buffer_degrees, min_lat - buffer_degrees,
                min_lat - buffer_degrees]

    # Add scatter trace for the points
    fig.add_trace(go.Scattermapbox(
        lat=df_points['latitude_IG'],
        lon=df_points['longitud_IG'],
        mode='markers',
        marker=dict(size=5, color='red'),
        name='Points',
        showlegend=False
    ))

    # this is the square
    fig.add_trace(
        go.Scattermapbox(
            lat=lats_box,
            lon=lons_box,
            mode="lines",
            line=dict(width=5, color='blue'),
            showlegend=False
        )
    )

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=10,
                      mapbox_center={
                          "lat": (max_lat + min_lat) / 2, "lon": (max_lon + min_lon) / 2},
                      )

    fig.write_html("C:\\Users\\JuanG\\Downloads\\mapa.html")
    fig = fig.to_html()

    return fig
