from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np

from ..models import MetodologiaResult

from .Bioacustica_Completo import (
    run_metodologia,
    guardado_cluster,
    run_metodologia_prueba,
)

from .utils import (
    prepare_csv_path,
    get_cluster_names_session,
    save_cluster_names_session
)

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_destination_folder_session,
    get_destination_folder_session,
    save_subfolders_details_session,
    get_subfolders_details_session,
    save_files_session,
    get_files_session,
    get_selected_subfolders_session,
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from .spectrogram_clusters import generate_spectrogram_with_clusters_plot, generate_spectrogram_representative_element_plot

from procesamiento.models import Progreso
import pandas as pd
from ecosonos.utils.tkinter_utils import get_root_folder, get_file
import asyncio
from asgiref.sync import sync_to_async


def toogle_div_visibility(request, data):
    div_type = request.POST.get("div")
    if div_type == "div_sonotipo":
        data['div_sonotipo'] = "block"
        data['div_reconocer'] = "none"
    else:
        data['div_sonotipo'] = "none"
        data['div_reconocer'] = "block"


async def load_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    await sync_to_async(toogle_div_visibility)(request, data)

    # Delete all records in the Progreso model
    await sync_to_async(Progreso.objects.all().delete)()

    try:
        # Get the root folder where the wav files are located
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # If no root folder is selected, render an error page or return an error response
    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Delete MetodologiaResult records if the request came from sonotipo, otherwise save cluster names to the session
    if data['div_sonotipo'] == 'block':
        await sync_to_async(MetodologiaResult.objects.all().delete)()
    else:
        selected_cluster_names = request.POST.getlist('clusters_names')
        await sync_to_async(save_cluster_names_session)(request, selected_cluster_names)
        data['selected_cluster_names'] = selected_cluster_names

    # Get lists of folder paths and their basenames that contain WAV files
    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folders_path': path,
            'folders_basename': basename,
        }
        folders_details.append(folder_detail)

    # Save root folder path and folder details to the session
    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')
    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    data['folders_details'] = folders_details

    # Save the statistics state and subfolder details to the session
    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def load_csv(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    await sync_to_async(toogle_div_visibility)(request, data)

    try:
        # Get the CSV file path
        csv_path = await sync_to_async(get_file)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Check if there was a selected file and contains a ".csv" extension
    if not csv_path or ".csv" not in csv_path:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Save the CSV file path to the session
    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    # Read the CSV file into a pandas DataFrame
    table = pd.read_csv(csv_path)
    table = table.to_numpy()
    cluster_names = 'Sp'

    try:
        # Get MetodologiaResult object obtained from running sonotipo
        metodologia = await sync_to_async(MetodologiaResult.objects.first)()
        mean_class = np.array(metodologia.mean_class)
        infoZC = np.array(metodologia.infoZC)
        representativo = np.array(metodologia.representativo)
        frecuencia = np.array(metodologia.frecuencia)
    except:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Generate new table with the values obtained from running sonotipo
    new_specs = await sync_to_async(guardado_cluster)(cluster_names, table, mean_class,
                                                      infoZC, representativo, frecuencia)

    # Extract cluster names from new_specs
    species_str = new_specs[0:, 0]
    species_str = [i[0] for i in species_str]

    data['cluster_names'] = species_str

    # Return the prepared data with the template for rendering
    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def prepare_destination_folder(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    await sync_to_async(toogle_div_visibility)(request, data)

    # Get the list of selected subfolders from the POST request
    selected_subdfolders = request.POST.getlist('carpetas')

    # Get the base names of selected subfolders
    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    try:
        # Get the destination folder where the processed output csv file will be saved
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    # If no destination folder is selected, return to the template
    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    # Save the destination folder and selected subfolders paths to the session
    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='etiquetado_auto')

    # Get folder details from the session
    folders_details = await sync_to_async(get_subfolders_details_session)(request, app='etiquetado_auto')

    data['carpetas_procesando'] = selected_subdfolders_base_name
    data['folders_details'] = folders_details
    data['seleccionadas'] = 'seleccionadas'

    # Delete only if the request was sent from sonotipo (check the div visibility)
    if data['div_reconocer'] == 'block':
        selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
        data['selected_cluster_names'] = selected_cluster_names

    # Return the prepared data with the template for rendering
    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def process_folders(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get selected subfolders from the session
    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request, app='etiquetado_auto')

    # If no subfolders are selected, return to the template
    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    # Get frequency range from POST request
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    await sync_to_async(toogle_div_visibility)(request, data)

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

    # Create a progress object to track the processing progress with the amount of files from the selected folders
    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(files_paths))

    # Get selected subfolders basenames
    selected_folders_basenames = get_subfolders_basename(
        selected_subdfolders)

    # Set parameters for processing
    canal = 1
    autosel = 0
    visualize = 0
    banda = [minimum_frequency, maximum_frequency]

    # Determine if this is for "sonotipo" or "reconocer" and prepare the CSV path accordingly
    table_type = 'sonotipo' if data['div_sonotipo'] == 'block' else 'reconocer'
    csv_path = prepare_csv_path(
        selected_folders_basenames, destination_folder, table_type)

    # Create a MetodologiaResult object for storing results
    metodologia_output = await sync_to_async(MetodologiaResult.objects.create)()

    data['carpetas_procesando'] = selected_folders_basenames

    if data['div_sonotipo'] == 'block':
        asyncio.create_task(run_metodologia(
            files_paths, files_basenames, banda, canal, autosel, visualize, progreso, csv_path, metodologia_output))
    else:
        # For "reconocer" mode, load the CSV table and run the metodologia prueba
        csv_path_sonotipo_table = await sync_to_async(get_csv_path_session)(request, app='etiquetado_auto')
        table = pd.read_csv(csv_path_sonotipo_table)
        table = table.to_numpy()
        cluster_names = 'Sp'

        try:
            # Get the MetodologiaResult object for the parameters
            metodologia = await sync_to_async(MetodologiaResult.objects.first)()
            mean_class = np.array(metodologia.mean_class)
            infoZC = np.array(metodologia.infoZC)
            representativo = np.array(metodologia.representativo)
            frecuencia = np.array(metodologia.frecuencia)
        except:
            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

        # Generate new spectrogram features using cluster information
        new_specs = await sync_to_async(guardado_cluster)(cluster_names, table, mean_class,
                                                          infoZC, representativo, frecuencia)

        # Get selected cluster names from the session
        selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
        data['selected_cluster_names'] = selected_cluster_names

        asyncio.create_task(run_metodologia_prueba(
            files_paths, files_basenames, banda, canal, new_specs, selected_cluster_names, progreso, csv_path))

    # Save the CSV path to the session
    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    data['mostrar_barra_proceso'] = True

    # Return the prepared data with the template for rendering
    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


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
    clusters = df.iloc[:, -1].unique().tolist()

    # Sort the cluster labels numerically
    data['clusters'] = sorted(clusters)
    data['files_details'] = files_details

    # Return the data as a JSON response
    return JsonResponse(data)
