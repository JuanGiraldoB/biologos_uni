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


def test(xlsx_path, sheet_name, latitud_field_name, longitud_field_name):
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


def get_conectivity_map_url(csv_path, latitud_field_name, longitud_field_name):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Extract latitudes and longitudes
    lats = df[latitud_field_name].dropna().values
    longs = df[longitud_field_name].dropna().values

    fig_urls = []

    # Iterate through the date columns
    for index, date_column in enumerate(df.columns[1:-2]):
        # Get values for the current date column
        values = df[date_column].dropna().values

        # Create a grid of lat/long values
        grid_lat, grid_long = np.mgrid[min(lats):max(
            lats):10j, min(longs):max(longs):10j]

        # Create an Ordinary Kriging object
        try:
            OK = OrdinaryKriging(
                longs, lats, values,
                variogram_model='gaussian',
                coordinates_type='geographic',
                verbose=True
            )
        except Exception as e:
            print(e)
            continue

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

        # Define a filename for the output TIFF and PNG files based on the date column
        tiff_filename = f'Colored_IDW_output_{index}.tif'
        png_filename = f'Colored_IDW_output_{index}.png'

        # Save the output TIFF file
        with rasterio.open(tiff_filename, 'w', driver='GTiff',
                           height=colored_data.shape[0], width=colored_data.shape[1], count=3, dtype=colored_data.dtype,
                           crs='+proj=latlong', transform=transform) as dst:
            for i in range(3):  # Write each channel (R, G, B)
                dst.write(colored_data[:, :, i], i+1)

        # Convert the TIFF to PNG
        with Image.open(tiff_filename) as im:
            im.save(png_filename)

        # Create a folium map with a satellite base layer
        m = folium.Map(location=[np.mean(lats), np.mean(longs)], zoom_start=13)
        #    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")

        # Create a FeatureGroup for the original points
        points_group = folium.FeatureGroup(name='Original Points', show=False)

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
                     image=png_filename,
                     bounds=[[min(lats), min(longs)], [max(lats), max(longs)]],
                     opacity=0.6, interactive=True).add_to(m)

        # Add a LayerControl to the map to toggle layers
        folium.LayerControl().add_to(m)

        # Define the relative and absolute paths for the HTML file based on the date column
        relative_path = os.path.join(
            'conectividad', 'plot', f'conectivity_plot_{index}.html')

        static_folder = os.path.join(
            settings.BASE_DIR, 'conectividad', 'static')

        fig_path = os.path.join(static_folder, relative_path)
        fig_url = static(relative_path)
        fig_urls.append(fig_url)

        # Save the HTML file
        m.save(fig_path)

    return fig_urls


if __name__ == '__main__':
    csv_path = "C:\\Users\\JuanG\\Downloads\\ZCR.csv"
    test(csv_path, "latitude_IG", "longitud_IG")
    # get_conectivity_map_url(csv_path)
