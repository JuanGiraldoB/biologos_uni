from django.shortcuts import render
import json
import os

from .constants import REEMPLAZO

from ecosonos.utils.session_utils import (
    save_root_folder_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session,
    save_csv_path_session,
    get_csv_path_session,
    get_files_session,
    save_files_session
)

from .spectograma import (
    calcular_espectrograma,
)

from ecosonos.utils.archivos_utils import (
    replace_char,
    add_row_csv,
    create_csv,
    add_row_csv,
)

from ecosonos.utils.carpeta_utils import (
    get_wav_files_in_folder
)

from ecosonos.utils.tkinter_utils import get_root_folder


def load_folder(request):
    try:
        # Get the root folder where the wav files are located
        root_folder = get_root_folder()
    except Exception as e:
        print("Error en cargar carpeta")
        return render(request, 'etiquetado/etiquetado.html')

    # If no root folder is selected, render an error page or return an error response
    if not root_folder:
        return render(request, 'etiquetado/etiquetado.html')

    # Save the root folder path to the session
    save_root_folder_session(
        request, root_folder, app="etiquetado")

    # Get lists of wav files paths and their basenames
    files_paths, files_basenames = get_wav_files_in_folder(root_folder)

    # Replace the directory separator character in file paths with a hyphen to be used in the url
    files_paths = replace_char(
        files_paths, caracter=os.sep, reemplazo=REEMPLAZO)

    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    # Save the file details to the session
    save_files_session(request, files_details, app='etiquetado')

    data = {
        "selected_folder": root_folder.split('/')[-1]
    }

    # data['archivos'] = zip(files_paths, files_basenames)

    # Return the prepared data with the template for rendering
    return render(request, 'etiquetado/etiquetado.html', data)


def prepare_destination_folder(request):
    data = {}

    try:
        # Get the destination folder where the CSV file will be created
        destination_folder = get_root_folder()
    except Exception as e:
        print("Error en cargar carpeta", e)
        return render(request, 'etiquetado/etiquetado.html')

    # If no destination folder is selected, render an error page or return an error response
    if not destination_folder:
        return render(request, 'etiquetado/etiquetado.html')

    # Extract the base name of the destination folder
    folder_basename = os.path.basename(destination_folder)

    # Create a CSV file in the destination folder with the same base name
    csv_path = create_csv(destination_folder, folder_basename)

    # Save the path to the CSV file to the session
    save_csv_path_session(request, csv_path)

    # Get the files from the session
    files_details = get_files_session(request, app='etiquetado')

    data['files_details'] = files_details
    data['selected_folder'] = get_root_folder_session(
        request, app="etiquetado").split('/')[-1]
    data['selected_destination_folder'] = destination_folder.split('/')[-1]

    # Return the prepared data with the template for rendering
    return render(request, 'etiquetado/etiquetado.html', data)


def prepare_label_data(request, path):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}

    # Get the files from the session
    files_details = get_files_session(request, app='etiquetado')

    # Extract the file paths from files_details
    files_paths = [file_path['path'] for file_path in files_details]

    # Replace the directory separator character in file paths
    replace_char(files_paths, caracter=os.sep, reemplazo=REEMPLAZO)

    data['ruta'] = path
    # Replace the auxiliar characters in 'path' with the correct directory separator
    path = path.replace(REEMPLAZO, os.sep)

    # Calculate the spectrogram for the given audio file
    f, t, s = calcular_espectrograma(path)

    # Convert and store frequency, time, and spectrogram data as lists in 'data'
    data['frequencies'] = f.tolist()
    data['times'] = t.tolist()
    data['spectrogram'] = s.tolist()

    # Extract and store the base name of the file in 'data'
    data['nombre'] = os.path.basename(path)

    data['files_details'] = files_details
    data['selected_folder'] = get_root_folder_session(
        request, app="etiquetado").split('/')[-1]
    data['selected_destination_folder'] = get_csv_path_session(
        request).split('/')[-2]

    return data


def label_data(request, path):
    data = prepare_label_data(request, path)
    return render(request, 'etiquetado/etiquetado.html', data)


def add_label(request, path, segement_data):
    file_name = os.path.basename(path)
    csv_path = get_csv_path_session(request)
    add_row_csv(csv_path, file_name,
                segement_data['etiqueta'],
                segement_data['x0'],
                segement_data['x1'],
                segement_data['y0'],
                segement_data['y1']
                )


def get_segment_data(request):
    data = json.loads(request.body)
    label = data.get('etiqueta')

    # Tiempos
    x0 = data.get('x0')
    x1 = data.get('x1')

    # Frecuencias
    y0 = data.get('y0')
    y1 = data.get('y1')

    segment_data = {
        'x0': x0,
        'x1': x1,
        'y0': y0,
        'y1': y1,
        'etiqueta': label
    }

    return segment_data
