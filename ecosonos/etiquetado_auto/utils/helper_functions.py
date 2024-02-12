from django.http import JsonResponse
import pandas as pd
import os
from django.conf import settings

from ..models import MetodologiaResult

from ecosonos.utils.session_utils import (
    get_csv_path_session,
    get_files_session,
)

from .plot_helper import (
    generate_spectrogram_with_clusters_plot,
    generate_spectrogram_representative_element_plot,
)


def spectrogram_plot(request):
    # Get the path to the CSV file from the session
    csv_path = get_csv_path_session(request, app='etiquetado_auto')

    # Get the selected clusters from the POST request and convert them to integers
    selected_clusters = request.POST.getlist('selected_clusters')
    selected_clusters = [int(cluster) for cluster in selected_clusters]

    # Get the file path from the POST request
    file_path = request.POST.get('path')

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Generate the spectrogram plot with selected clusters
    plot_url = generate_spectrogram_with_clusters_plot(
        file_path, selected_clusters, df)

    # Return the plot URL as a JSON response
    return JsonResponse({'plot_url': plot_url})


def representative_element_plot(request):
    # Get the list of representative element indices from the POST request
    representativo_index = request.POST.getlist('representativo')

    # Get the path to the CSV file from the session
    csv_path = get_csv_path_session(request, app='etiquetado_auto')

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Get the first representative index as an integer
    representative_index = int(representativo_index[0])

    # Get the MetodologiaResult object obtained from runing sonotipo
    metodologia_output = MetodologiaResult.objects.first()

    # Generate the representative element plot
    plot_url = generate_spectrogram_representative_element_plot(
        metodologia_output, df, representative_index)

    # Return the plot URL as a JSON response
    return JsonResponse({'plot_url': plot_url})


def get_spectrogram_data(request):
    # Create an empty dictionary to store the data to be sent as a JSON response
    data = {}

    # Get the files details from the session
    files_details = get_files_session(request, app='etiquetado_auto')

    # Get the path to the CSV file from the session
    csv_path = get_csv_path_session(request, app='etiquetado_auto')

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Get unique cluster labels from the last column of the DataFrame
    clusters = df.iloc[:, -2].unique().tolist()

    # Sort the cluster labels numerically
    data['clusters'] = sorted(clusters)
    data['files_details'] = files_details

    # Return the data as a JSON response
    return JsonResponse(data)


def get_hourly_sonotype_plots_urls():
    img_dir = os.path.join(settings.BASE_DIR, 'etiquetado_auto', 'static',
                           'etiquetado_auto', 'img')

    # Get a list of image file names in the directory
    img_file_names = [f for f in os.listdir(
        img_dir) if f.lower().endswith(('.png'))]

    # Construct the URLs for each image
    img_urls = [os.path.join(
        settings.STATIC_URL, 'etiquetado_auto', 'img', fname) for fname in img_file_names]

    return JsonResponse({"img_urls": img_urls})
