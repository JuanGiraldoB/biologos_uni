import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin
from folium.raster_layers import ImageOverlay
import folium
from pykrige.ok import OrdinaryKriging
import matplotlib.pyplot as plt
from PIL import Image
from django.templatetags.static import static
from django.conf import settings
import os


def get_conectivity_map_url(xlsx_path, sheet_name, latitud_field_name, longitud_field_name):
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)

    lats = df[latitud_field_name].dropna().values
    longs = df[longitud_field_name].dropna().values

    values = np.random.rand(len(lats))

    # Create a grid of lat/long values
    grid_lat, grid_long = np.mgrid[min(lats):max(
        lats):10j, min(longs):max(longs):10j]

    # Create an Ordinary Kriging object
    OK = OrdinaryKriging(
        longs, lats, values,
        variogram_model='gaussian',
        coordinates_type='geographic',
        verbose=True
    )

    z, _ = OK.execute('grid', grid_long, grid_lat)

    grid_z = z[0].reshape(grid_lat.shape)

    # Create a grid of lat/long values
    grid_lat, grid_long = np.mgrid[min(lats):max(
        lats):100j, min(longs):max(longs):100j]
    # Perform IDW interpolation
    grid_z = griddata((lats, longs), values,
                      (grid_lat, grid_long), method='nearest')

    # 1. Scale the data to 0-255
    scaled_data = ((grid_z - grid_z.min()) / (grid_z.max() -
                   grid_z.min()) * 255).astype(np.uint8)

    # 2. Apply a colormap (this will give an RGBA image, but we'll use RGB)
    # Using the viridis colormap
    colored_data = plt.cm.viridis(scaled_data)[:, :, :3]
    # Convert to 8-bit RGB
    colored_data = (colored_data * 255).astype(np.uint8)

    transform = from_origin(grid_long[0][0], grid_lat[0][0], abs(
        grid_long[0][0]-grid_long[1][0]), abs(grid_lat[0][0]-grid_lat[1][0]))
    with rasterio.open('Colored_IDW_output.tif', 'w', driver='GTiff',
                       height=colored_data.shape[0], width=colored_data.shape[1], count=3, dtype=colored_data.dtype,
                       crs='+proj=latlong', transform=transform) as dst:
        for i in range(3):  # Write each channel (R, G, B)
            dst.write(colored_data[:, :, i], i+1)

    # Convert the TIFF to PNG
    with Image.open('Colored_IDW_output.tif') as im:
        im.save('Colored_IDW_output.png')

    # Create a folium map with a satellite base layer
    m = folium.Map(location=[np.mean(lats), np.mean(longs)], zoom_start=10,
                   tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")

    # Create a FeatureGroup for the original points
    points_group = folium.FeatureGroup(name='Original Points')

    # Add the original lat/long points to the FeatureGroup
    for lat, long in zip(lats, longs):
        folium.Marker(
            [lat, long],
            tooltip="Lat: {} Long: {}".format(lat, long)
        ).add_to(points_group)

    # Add the FeatureGroup to the map
    points_group.add_to(m)

    # Add the interpolated heatmap overlay (now using the PNG)
    ImageOverlay(name='Interpolated Data',
                 image='Colored_IDW_output.png',
                 bounds=[[min(lats), min(longs)], [max(lats), max(longs)]],
                 opacity=0.6, interactive=True).add_to(m)

    # Add a LayerControl to the map to toggle layers
    folium.LayerControl().add_to(m)

    relative_path = os.path.join(
        'conectividad', 'plot', 'conectivity_plot.html')

    static_folder = os.path.join(
        settings.BASE_DIR, 'conectividad', 'static')

    fig_path = os.path.join(static_folder, relative_path)

    fig_url = static(relative_path)

    m.save(fig_path)
    return fig_url


if __name__ == '__main__':
    csv_path = "C:\\Users\\JuanG\\Downloads\\UDAS Pasivo_20221001_Zamuro.xlsx"
    get_conectivity_map_url(csv_path)
