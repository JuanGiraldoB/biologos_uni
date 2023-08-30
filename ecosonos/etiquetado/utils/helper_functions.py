from django.shortcuts import render
import json
import os

from ecosonos.utils.session_utils import (
    save_root_folder_session,
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
    get_files_in_folder
)

from ecosonos.utils.tkinter_utils import get_root_folder


def load_folder(request):
    try:
        root_folder = get_root_folder()
    except Exception as e:
        print("Error en cargar carpeta")
        return render(request, 'etiquetado/etiquetado.html')

    if not root_folder:
        return render(request, 'etiquetado/etiquetado.html')

    save_root_folder_session(
        request, root_folder, app="etiquetado")

    files_paths, files_basenames = get_files_in_folder(root_folder)

    files_paths = replace_char(files_paths, caracter=os.sep, reemplazo='-')

    files_details = []
    for path, basename in zip(files_paths, files_basenames):
        file_details = {
            'path': path,
            'basename': basename
        }

        files_details.append(file_details)

    save_files_session(request, files_details, app='etiquetado')

    # data['archivos'] = zip(files_paths, files_basenames)

    return render(request, 'etiquetado/etiquetado.html')


def prepare_destination_folder(request):
    data = {}

    try:
        destination_folder = get_root_folder()
    except Exception as e:
        print("Error en cargar carpeta", e)
        return render(request, 'etiquetado/etiquetado.html')

    if not destination_folder:
        return render(request, 'etiquetado/etiquetado.html')

    folder_basename = os.path.basename(destination_folder).split(".")[0]

    csv_path = create_csv(destination_folder, folder_basename)
    save_csv_path_session(request, csv_path)

    files_details = get_files_session(request, app='etiquetado')
    data['files_details'] = files_details

    return render(request, 'etiquetado/etiquetado.html', data)


def prepare_label_data(request, path):
    files_details = get_files_session(request, app='etiquetado')
    files_paths = [file_path['path'] for file_path in files_details]

    replace_char(files_paths, caracter=os.sep, reemplazo='-')

    data = {}
    data['ruta'] = path
    path = path.replace('-', os.sep)

    f, t, s = calcular_espectrograma(path)

    data['frequencies'] = f.tolist()
    data['times'] = t.tolist()
    data['spectrogram'] = s.tolist()
    data['nombre'] = os.path.basename(path)
    data['files_details'] = files_details

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
