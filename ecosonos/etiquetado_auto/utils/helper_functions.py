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

from .spectrogram_clusters import generate_spectrogram_with_clusters_plot, generate_representative_element_plot

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
    data = {}

    await sync_to_async(toogle_div_visibility)(request, data)

    try:
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(Progreso.objects.all().delete)()

    # Delete only if the request was sent from sonotipo
    if data['div_sonotipo'] == 'block':
        await sync_to_async(MetodologiaResult.objects.all().delete)()
    else:
        selected_cluster_names = request.POST.getlist('clusters_names')
        await sync_to_async(save_cluster_names_session)(request, selected_cluster_names)
        data['selected_cluster_names'] = selected_cluster_names

    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folders_path': path,
            'folders_basename': basename,
        }
        folders_details.append(folder_detail)

    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')
    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    data['folders_details'] = folders_details

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def load_csv(request):
    data = {}

    await sync_to_async(toogle_div_visibility)(request, data)

    try:
        csv_path = await sync_to_async(get_file)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    if not csv_path or ".csv" not in csv_path:
        print("x")
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    table = pd.read_csv(csv_path)
    table = table.to_numpy()
    cluster_names = 'Sp'
    metodologia = await sync_to_async(MetodologiaResult.objects.first)()
    mean_class = np.array(metodologia.mean_class)
    infoZC = np.array(metodologia.infoZC)
    representativo = np.array(metodologia.representativo)
    frecuencia = np.array(metodologia.frecuencia)
    new_specs = await sync_to_async(guardado_cluster)(cluster_names, table, mean_class,
                                                      infoZC, representativo, frecuencia)

    species_str = new_specs[0:, 0]
    species_str = [i[0] for i in species_str]

    data['cluster_names'] = species_str

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def prepare_destination_folder(request):
    data = {}

    selected_subdfolders = request.POST.getlist('carpetas')

    selected_subdfolders_base_name = get_subfolders_basename(
        selected_subdfolders)

    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(toogle_div_visibility)(request, data)

    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    await sync_to_async(save_selected_subfolders_session)(request, selected_subdfolders,  app='etiquetado_auto')
    folders_details = await sync_to_async(get_subfolders_details_session)(request, app='etiquetado_auto')

    data['carpetas_procesando'] = selected_subdfolders_base_name
    data['folders_details'] = folders_details
    data['seleccionadas'] = 'seleccionadas'

    # Delete only if the request was sent from sonotipo
    if data['div_reconocer'] == 'block':
        selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
        data['selected_cluster_names'] = selected_cluster_names

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def process_folders(request):
    data = {}

    selected_subdfolders = await sync_to_async(get_selected_subfolders_session)(request, app='etiquetado_auto')
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    await sync_to_async(toogle_div_visibility)(request, data)

    if minimum_frequency:
        minimum_frequency = int(minimum_frequency)
    else:
        minimum_frequency = 'min'

    if maximum_frequency:
        maximum_frequency = int(maximum_frequency)
    else:
        maximum_frequency = 'max'

    if not selected_subdfolders:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado_auto')

    files_paths, files_basenames = get_all_files_in_all_folders(
        selected_subdfolders)

    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    save_files_session(request, files_details, app='etiquetado_auto')

    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(files_paths))

    selected_folders_basenames = get_subfolders_basename(
        selected_subdfolders)

    canal = 1
    autosel = 0
    visualize = 0
    banda = [minimum_frequency, maximum_frequency]

    table_type = 'sonotipo' if data['div_sonotipo'] == 'block' else 'reconocer'

    csv_path = prepare_csv_path(
        selected_folders_basenames, destination_folder, table_type)

    metodologia_output = await sync_to_async(MetodologiaResult.objects.create)()
    data['carpetas_procesando'] = selected_folders_basenames

    if data['div_sonotipo'] == 'block':
        asyncio.create_task(run_metodologia(
            files_paths, files_basenames, banda, canal, autosel, visualize, progreso, csv_path, metodologia_output))
    else:
        csv_path_sonotipo_table = await sync_to_async(get_csv_path_session)(request, app='etiquetado_auto')
        table = pd.read_csv(csv_path_sonotipo_table)
        table = table.to_numpy()
        cluster_names = 'Sp'
        metodologia = await sync_to_async(MetodologiaResult.objects.first)()
        mean_class = np.array(metodologia.mean_class)
        infoZC = np.array(metodologia.infoZC)
        representativo = np.array(metodologia.representativo)
        frecuencia = np.array(metodologia.frecuencia)
        new_specs = await sync_to_async(guardado_cluster)(cluster_names, table, mean_class,
                                                          infoZC, representativo, frecuencia)

        selected_cluster_names = await sync_to_async(get_cluster_names_session)(request)
        data['selected_cluster_names'] = selected_cluster_names

        asyncio.create_task(run_metodologia_prueba(
            files_paths, files_basenames, banda, canal, new_specs, selected_cluster_names, progreso, csv_path))

    await sync_to_async(save_csv_path_session)(
        request, csv_path, app='etiquetado_auto')

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


def spectrogram_plot(request):
    csv_path = get_csv_path_session(request, app='etiquetado_auto')
    selected_clusters = request.POST.getlist('selected_clusters')
    selected_clusters = [int(cluster) for cluster in selected_clusters]
    file_path = request.POST.get('path')

    df = pd.read_csv(csv_path)
    plot_url = generate_spectrogram_with_clusters_plot(
        file_path, selected_clusters, df)

    return JsonResponse({'plot_url': plot_url})


def representative_element_plot(request):
    representativo_index = request.POST.getlist('representativo')
    csv_path = get_csv_path_session(request, app='etiquetado_auto')

    df = pd.read_csv(csv_path)
    metodologia_output = MetodologiaResult.objects.first()
    plot_url = generate_representative_element_plot(
        metodologia_output, df, int(representativo_index[0]))

    return JsonResponse({'plot_url': plot_url})


def get_spectrogram_data(request):
    data = {}
    files_details = get_files_session(request, app='etiquetado_auto')

    csv_path = get_csv_path_session(request, app='etiquetado_auto')
    print(f'csv_path: {csv_path} - ************')
    print()
    print(f'files_details: {files_details} - ************')
    df = pd.read_csv(csv_path)

    clusters = df.iloc[:, -1].unique().tolist()

    data['clusters'] = sorted(clusters)
    data['files_details'] = files_details

    return JsonResponse(data)
