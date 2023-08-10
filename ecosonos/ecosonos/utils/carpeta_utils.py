import os
import platform
from concurrent.futures import ThreadPoolExecutor


from .archivos_utils import (
    get_date_range_from_filenames,
    get_files_range_length
)


def abrir_administrador_archivos(carpeta):
    sistema_operativo = platform.system()

    try:
        if sistema_operativo == "Windows":
            os.system(f'start {carpeta}')
        elif sistema_operativo == "Linux":
            os.system(f'xdg-open {carpeta}')
        elif sistema_operativo == "Darwin":
            os.system(f'open {carpeta}')
        else:
            print("Unknown OS")
    except Exception as e:
        print(f"An error occurred: {e}")


def obtener_subcarpetas(carpeta):
    carpetas_nombre_completo = []
    carpetas_nombre_base = []

    carpetas_nombre_completo.append(carpeta)
    carpetas_nombre_base.append(os.path.basename(carpeta))

    for ruta, carpetas_subdir, _ in os.walk(carpeta):
        for carpeta_subdir in carpetas_subdir:
            nombre_completo = os.path.join(
                ruta, carpeta_subdir)  # .replace(os.path.sep, '/')
            carpetas_nombre_completo.append(nombre_completo)

            nombre_base = os.path.basename(os.path.join(ruta, carpeta_subdir))
            carpetas_nombre_base.append(nombre_base)

    return carpetas_nombre_completo, carpetas_nombre_base


def obtener_cantidad_archivos_por_subdir(carpetas):
    carpetas_cantidad_archivos = []

    for carpeta in carpetas:
        ruta_carpeta = os.path.join(carpeta, carpeta)
        archivos_carpeta = [archivo for archivo in os.listdir(
            ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, archivo))]
        cantidad_archivos = len(archivos_carpeta)
        carpetas_cantidad_archivos.append(cantidad_archivos)

    return carpetas_cantidad_archivos


def obtener_nombres_base(carpetas):
    nombres_base = [os.path.basename(carpeta) for carpeta in carpetas]
    return nombres_base


def selecciono_carpeta(carpeta_raiz):
    """
        Verifica si fue seleccionada una carpeta
    """
    return not carpeta_raiz


def subcarpetas_seleccionadas(carpetas):
    """
        Verifica si existen carpetas seleccionadas
    """
    return not carpetas


# def save_root_folder_session(request, raiz, app='preproceso'):
#     if app == 'indices':
#         request.session['raiz_indices'] = raiz
#     elif app == 'etiquetado':
#         request.session['raiz_etiquetado'] = raiz
#     elif app == 'etiquetado-auto':
#         request.session['raiz_etiquetado_auto'] = raiz
#     else:
#         request.session['raiz_preproceso'] = raiz


# def get_root_folder_session(request, app='preproceso'):
#     if app == 'indices':
#         return request.session['raiz_indices']
#     elif app == 'etiquetado':
#         return request.session['raiz_etiquetado']
#     elif app == 'etiquetado-auto':
#         return request.session['raiz_etiquetado_auto']

#     return request.session['raiz_preproceso']


# def save_selected_subfolders_session(request, carpetas, app='preproceso'):
#     if app == 'indices':
#         request.session['carpetas_indices'] = carpetas
#     elif app == 'etiquetado-auto':
#         request.session['carpetas_etiquetado_auto'] = carpetas
#     else:
#         request.session['carpetas_preproceso'] = carpetas


# def get_selected_subfolders_session(request, app='preproceso'):
#     if app == 'indices':
#         return request.session['carpetas_indices']

#     return request.session['carpetas_preproceso']


def cambiar_diagonales_carpeta(carpeta):
    return carpeta.replace('\\', '/')


# def save_csv_path_session(request, ruta_csv):
#     request.session['csv_etiquetado'] = ruta_csv


# def get_csv_path_session(request):
#     return request.session['csv_etiquetado']


# def guardar_ruta_csv_session(request, ruta_csv, app='preproceso'):
#     if app == 'etiquetado':
#         request.session['csv_etiquetado'] = ruta_csv
#     elif app == 'etiquetado-auto':
#         request.session['csv_etiquetado_auto'] = ruta_csv


# def obtener_ruta_csv_session(request, app='preproceso'):
#     if app == 'etiquetado':
#         return request.session['csv_etiquetado']
#     elif app == 'etiquetado-auto':
#         return request.session['csv_etiquetado_auto']

def get_folders_with_wav(folder, file_extension='.wav'):
    subfolders_wav_path = []
    subfolders_wav_basename = []

    # Checks if the root folder has .wav files
    if any(file.lower().endswith(file_extension) for file in os.listdir(folder)):
        subfolders_wav_path.append(folder)

    for root, subdirs, _ in os.walk(folder):
        for subdir in subdirs:
            subdir_path = os.path.join(root, subdir)

            if any(file.lower().endswith(file_extension) for file in os.listdir(subdir_path)):
                subfolders_wav_path.append(subdir_path)
                subfolders_wav_basename.append(subdir)

    return subfolders_wav_path, subfolders_wav_basename


def get_subfolders_basename(folders):
    folders_basename = [os.path.basename(folder) for folder in folders]
    return folders_basename


def get_folders_details(folders):
    folder_details = []

    # for folder in folders:
    #     folder_details.append(get_folder_detail(folder))

    with ThreadPoolExecutor() as executor:
        folder_details = list(executor.map(get_folder_detail, folders))

    return folder_details


def get_folder_detail(folder):
    files_path, files_base_name = get_files_in_folder(folder)
    number_of_files = len(files_base_name)
    range_of_dates = get_date_range_from_filenames(files_base_name)
    range_of_lengths = get_files_range_length(files_path)

    folder_detail = {
        'folder_name': os.path.basename(folder),
        'folder_path': folder,
        'files_path': files_path,
        'files_base_name': files_base_name,
        'number_of_files': number_of_files,
        'range_of_dates': range_of_dates,
        'range_of_lengths': range_of_lengths
    }

    return folder_detail


def get_files_in_folder(folder, file_extension='.wav'):
    files_path = []
    files_base_name = []

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)

        if os.path.isfile(file_path) and file.lower().endswith(file_extension):
            files_path.append(file_path)
            files_base_name.append(file)

    return files_path, files_base_name
