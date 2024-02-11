from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import os
from django.conf import settings


from ..models import MetodologiaResult, GuardadoClusterResult

from .Bioacustica_Completo import (
    guardado_cluster,
    run_metodologia_prueba,
)

from .utils import (
    get_cluster_names_session,
    save_cluster_names_session,
    serialize_and_save_to_db,
    deserialize_from_db
)

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_destination_folder_session,
    get_destination_folder_session,
    save_subfolders_details_session,
    save_files_session,
    get_files_session,
    get_selected_subfolders_session,
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from .plot_helper import (
    generate_spectrogram_with_clusters_plot,
    generate_spectrogram_representative_element_plot,
    run_generate_hourly_pattern_graph_of_the_sonotype
)
from procesamiento.models import Progreso
import pandas as pd
from ecosonos.utils.tkinter_utils import get_root_folder, get_file
import asyncio
from asgiref.sync import sync_to_async


async def load_main_folder_reconocer(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Delete all records in the Progreso model
    await sync_to_async(Progreso.objects.all().delete)()

    try:
        # Get the root folder where the wav files are located
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # If no root folder is selected, render an error page or return an error response
    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Save cluster names to the session
    selected_cluster_names = request.POST.getlist('clusters_names')
    await sync_to_async(save_cluster_names_session)(request, selected_cluster_names)
    data['selected_cluster_names'] = selected_cluster_names

    # Get lists of folder paths and their basenames that contain WAV files
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folder_path': path,
            'folder_name': basename,
        }
        folders_details.append(folder_detail)

    # Save root folder path and folder details to the session
    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')
    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    data['folders_details'] = folders_details

    return JsonResponse(data)
    # Save the statistics state and subfolder details to the session
    # return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)


async def load_csv_reconocer(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    try:
        # Get the CSV file path
        csv_path = await sync_to_async(get_file)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Check if there was a selected file and contains a ".csv" extension
    if not csv_path or ".csv" not in csv_path:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Save the CSV file path to the session
    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    # Read the CSV file into a pandas DataFrame
    table = pd.read_csv(csv_path)
    del table['Membership']
    table = table.to_numpy()
    cluster_names = 'Sp'

    try:
        # Get MetodologiaResult object obtained from running sonotipo
        metodologia = await sync_to_async(MetodologiaResult.objects.first)()
        mean_class = np.array(metodologia.mean_class)
        infoZC = np.array(metodologia.infoZC)
        representativo = np.array(metodologia.representativo)
        frecuencia = np.array(metodologia.frecuencia)
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Generate new table with the values obtained from running sonotipo
    new_specs = await sync_to_async(guardado_cluster)(cluster_names, table, mean_class,
                                                      infoZC, representativo, frecuencia)

    await sync_to_async(GuardadoClusterResult.objects.all().delete)()
    await sync_to_async(serialize_and_save_to_db)(new_specs)

    # Extract cluster names from new_specs
    species_str = new_specs[0:, 0]
    species_str = [i[0] for i in species_str]

    data['cluster_names'] = species_str

    return JsonResponse(data)
    # Return the prepared data with the template for rendering
    # return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)


async def prepare_destination_folder_reconocer(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the list of selected subfolders from the POST request
    selected_subdfolders = request.POST.getlist('carpetas')

    # Get the base names of selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html")

    try:
        # Get the destination folder where the processed output csv file will be saved
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html")

    # If no destination folder is selected, return to the template
    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html")

    # Save the destination folder and selected subfolders paths to the session
    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='etiquetado_auto')

    selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)

    data['folders'] = selected_subdfolders_base_name
    data['selected_cluster_names'] = selected_cluster_names
    data['destination_folder'] = destination_folder.split('/')[-1]

    return JsonResponse(data)
    # Return the prepared data with the template for rendering
    # return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)


async def process_folders_reconocer(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get selected subfolders from the session
    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request, app='etiquetado_auto')

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Get frequency range from POST request
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    # Check and set minimum and maximum frequency values
    if minimum_frequency:
        minimum_frequency = int(minimum_frequency)
    else:
        minimum_frequency = 'min'

    if maximum_frequency:
        maximum_frequency = int(maximum_frequency)
    else:
        maximum_frequency = 'max'

    # Get the destination folder from the session
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado_auto')

    # Get all file paths and basenames from the selected subfolders
    files_paths, files_basenames = get_all_files_in_all_folders(
        selected_subdfolders)

    # Prepare file details for rendering in the template
    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    # Save file details to the session
    save_files_session(request, files_details, app='etiquetado_auto')

    # Calculate the 1% of total files
    one_percent = int(0.01 * len(files_paths))

    # Create a progress object to track the processing progress with the amount of files from the selected folders
    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(files_paths) + one_percent, uno_porciento=one_percent)

    # Get selected subfolders basenames
    selected_folders_basenames = get_subfolders_basename(
        selected_subdfolders)

    # Set parameters for processing
    canal = 1
    banda = [minimum_frequency, maximum_frequency]

    csv_name = 'Tabla_reconocimiento.csv'
    csv_path = os.path.join(destination_folder, csv_name)

    data['carpetas_procesando'] = selected_folders_basenames

    # Load the CSV table and run the metodologia prueba
    csv_path_sonotipo_table = await sync_to_async(get_csv_path_session)(request, app='etiquetado_auto')
    table = pd.read_csv(csv_path_sonotipo_table)
    del table['Membership']
    table = table.to_numpy()

    new_specs = await sync_to_async(deserialize_from_db)()

    # Get selected cluster names from the session
    selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
    data['selected_cluster_names'] = selected_cluster_names

    asyncio.create_task(run_metodologia_prueba(
        files_paths, files_basenames, banda, canal, new_specs, selected_cluster_names, progreso, csv_path))

    # Save the CSV path to the session
    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    data['mostrar_barra_proceso'] = True
    data['button_disable'] = "disabled"

    # Return the prepared data with the template for rendering
    return JsonResponse(data)
    # return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)


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


async def process_hourly_sonotype(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    try:
        # Get the CSV file path
        csv_path = await sync_to_async(get_file)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    # Check if there was a selected file and contains a ".csv" extension
    if not csv_path or ".csv" not in csv_path:
        return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)

    dft = pd.read_csv(csv_path)
    unique_clusters = list(dft['Cluster'].unique())
    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(unique_clusters))
    asyncio.create_task(
        run_generate_hourly_pattern_graph_of_the_sonotype(dft, progreso))

    data['mostrar_barra_proceso'] = True

    return render(request, "etiquetado_auto/etiquetado_auto_reconocer_ajax.html", data)


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
