from django.shortcuts import render
from django.http import JsonResponse

from ..models import MetodologiaResult

from .Bioacustica_Completo import (
    run_metodologia
)

from .utils import prepare_csv_table_name

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
    get_files_session
)

from ecosonos.utils.carpeta_utils import (
    get_subfolders_basename,
    get_folders_with_wav,
    get_all_files_in_all_folders
)

from .spectrogram_clusters import generate_spectrogram_with_clusters_plot, generate_representative_element_plot

from procesamiento.models import Progreso
import pandas as pd
from ecosonos.utils.tkinter_utils import get_root_folder
import asyncio
from asgiref.sync import sync_to_async


async def load_folder(request):
    data = {}

    div_type = request.POST.get("div")
    if div_type == "div_sonotipo":
        data['div_sonotipo'] = "block"
        data['div_reconocer'] = "none"
    else:
        data['div_sonotipo'] = "none"
        data['div_reconocer'] = "block"

    try:
        root_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    if not root_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(save_root_folder_session)(request, root_folder, app='etiquetado_auto')

    await sync_to_async(Progreso.objects.all().delete)()
    await sync_to_async(MetodologiaResult.objects.all().delete)()

    folders_wav_path, folders_wav_basename = get_folders_with_wav(
        root_folder)

    folders_details = []
    for path, basename in zip(folders_wav_path, folders_wav_basename):
        folder_detail = {
            'folders_path': path,
            'folders_basename': basename,
        }
        folders_details.append(folder_detail)

    await sync_to_async(save_subfolders_details_session)(request, folders_details, app='etiquetado_auto')

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def prepare_destination_folder(request):
    data = {}

    div_type = request.POST.get("div")
    if div_type == "div_sonotipo":
        data['div_sonotipo'] = "block"
        data['div_reconocer'] = "none"
    else:
        data['div_sonotipo'] = "none"
        data['div_reconocer'] = "block"

    try:
        destination_folder = await sync_to_async(get_root_folder)()
    except Exception as e:
        print("Error en destino carpeta", e)
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    if not destination_folder:
        return render(request, "etiquetado_auto/etiquetado-auto.html")

    await sync_to_async(save_destination_folder_session)(request, destination_folder, app="etiquetado_auto")
    folders_details = await sync_to_async(get_subfolders_details_session)(request, app='etiquetado_auto')

    data['folders_details'] = folders_details

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


async def process_folders(request):
    data = {}

    selected_folders = request.POST.getlist('carpetas')
    minimum_frequency = request.POST.get('frecuenciaminima')
    maximum_frequency = request.POST.get('frecuenciamaxima')

    div_type = request.POST.get("div")
    if div_type == "div_sonotipo":
        data['div_sonotipo'] = "block"
        data['div_reconocer'] = "none"
    else:
        data['div_sonotipo'] = "none"
        data['div_reconocer'] = "block"

    if minimum_frequency:
        minimum_frequency = int(minimum_frequency)
    else:
        minimum_frequency = 'min'

    if maximum_frequency:
        maximum_frequency = int(maximum_frequency)
    else:
        maximum_frequency = 'max'

    if not selected_folders:
        return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    await sync_to_async(save_selected_subfolders_session)(request, selected_folders,  app='etiquetado_auto')
    destination_folder = await sync_to_async(get_destination_folder_session)(request, app='etiquetado_auto')

    files_paths, files_basenames = get_all_files_in_all_folders(
        selected_folders)

    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    save_files_session(request, files_details, app='etiquetado_auto')

    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(files_paths))
    metodologia_output = await sync_to_async(MetodologiaResult.objects.create)()

    selected_folders_basenames = get_subfolders_basename(
        selected_folders)

    canal = 1
    autosel = 0
    visualize = 0
    banda = [minimum_frequency, maximum_frequency]

    csv_name = prepare_csv_table_name(
        selected_folders_basenames, destination_folder)
    await sync_to_async(save_csv_path_session)(
        request, csv_name)

    asyncio.create_task(run_metodologia(
        files_paths, files_basenames, banda, canal, autosel, visualize, progreso, csv_name, metodologia_output))

    data['carpetas_procesando'] = selected_folders_basenames

    return render(request, "etiquetado_auto/etiquetado-auto.html", data)


def spectrogram_plot(request):
    csv_path = get_csv_path_session(request)
    selected_clusters = request.POST.getlist('selected_clusters')
    selected_clusters = [int(cluster) for cluster in selected_clusters]
    file_path = request.POST.get('path')

    df = pd.read_csv(csv_path)
    plot_url = generate_spectrogram_with_clusters_plot(
        file_path, selected_clusters, df)

    metodologia_output = MetodologiaResult.objects.first()
    generate_representative_element_plot(file_path, metodologia_output, df)

    return JsonResponse({'plot_url': plot_url})


def get_spectrogram_data(request):
    data = {}
    files_details = get_files_session(request, app='etiquetado_auto')

    csv_path = get_csv_path_session(request)
    df = pd.read_csv(csv_path)

    clusters = df.iloc[:, -1].unique().tolist()

    data['clusters'] = sorted(clusters)
    data['files_details'] = files_details

    return JsonResponse(data)
