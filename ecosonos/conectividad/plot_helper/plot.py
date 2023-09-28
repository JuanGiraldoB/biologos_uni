import pandas as pd
import numpy as np

import plotly.graph_objects as go


def create_map(departamentos, df_points):
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
    # fig.add_trace(go.Scattermapbox(
    #     lat=df_points['latitude_IG'],
    #     lon=df_points['longitud_IG'],
    #     mode='markers',
    #     marker=dict(size=5, color='red'),
    #     name='Points',
    #     showlegend=False
    # ))

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

    # Add all border traces to the figure
    # border_traces = obtener_bordes_colombia(departamentos)
    # fig.add_traces(border_traces)

    random_values = np.random.uniform(0, 1, len(df_points['latitude_IG']))

    # Create a heatmap trace with random values
    heatmap_trace = go.Densitymapbox(
        lat=df_points['latitude_IG'],
        lon=df_points['longitud_IG'],
        z=random_values,
        radius=20,
        showscale=True,
        colorscale='Viridis',
        colorbar_title='Heatmap Intensity',
        opacity=1,
    )

    # Add the heatmap trace to the figure
    fig.add_trace(heatmap_trace)

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_accesstoken='pk.eyJ1IjoibWF4cm9ja2V0IiwiYSI6ImNsbjBxdWQwaTFxc2UyanQzaWJmMHEyMzIifQ.1gUmlIl8TbjowZyfurGLOA',
                      mapbox_zoom=10,
                      mapbox_center={
                          "lat": (max_lat + min_lat) / 2, "lon": (max_lon + min_lon) / 2},
                      )

    fig.write_html("C:\\Users\\JuanG\\Downloads\\mapa.html")
    fig = fig.to_html()

    return fig


def obtener_bordes_colombia(departamentos):
    border_traces = []

    # Iterate over each departamento feature in the JSON data
    for feature in departamentos['features']:
        # Extract the departamento code and border coordinates
        dpto_code = feature['properties']['DPTO']
        border_coords = feature['geometry']['coordinates'][0]

        # Create a trace for the departamento border
        border_trace = go.Scattermapbox(
            lat=[coord[1] for coord in border_coords],
            lon=[coord[0] for coord in border_coords],
            mode='lines',
            line=dict(color='green', width=1),
            showlegend=False,
            name=dpto_code
        )

        # Add the border trace to the list
        border_traces.append(border_trace)

    return border_traces
