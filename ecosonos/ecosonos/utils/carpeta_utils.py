import os
import platform
import pathlib
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
                ruta, carpeta_subdir)
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


def get_folders_with_wav(folder, file_extension='.wav'):
    subfolders_wav_path = []
    subfolders_wav_basename = []

    # Checks if the root folder has .wav files
    if any(file.lower().endswith(file_extension) for file in os.listdir(folder)):
        subfolders_wav_path.append(folder)
        subfolders_wav_basename.append(os.path.basename(folder))

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

    with ThreadPoolExecutor() as executor:
        folder_details = list(executor.map(get_folder_detail, folders))

    return folder_details


def get_folder_detail(folder):
    files_path, files_base_name = get_wav_files_in_folder(folder)
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


def get_all_files_in_all_folders(folders):
    all_files_path = []
    all_files_path_basename = []

    for folder in folders:
        files_path, files_basename = get_wav_files_in_folder(folder)
        all_files_path.extend(files_path)
        all_files_path_basename.extend(files_basename)

    return all_files_path, all_files_path_basename


def get_wav_files_in_folder(folder, file_extension='.wav'):
    files_path = []
    files_basename = []

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)

        if os.path.isfile(file_path) and file.lower().endswith(file_extension):
            files_path.append(str(pathlib.Path(file_path)))
            files_basename.append(file)

    return files_path, files_basename
