import os
import platform


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


def guardar_raiz_carpeta_session(request, raiz, app='preproceso'):
    if app == 'indices':
        request.session['raiz_indices'] = raiz
    elif app == 'etiquetado':
        request.session['raiz_etiquetado'] = raiz
    elif app == 'etiquetado-auto':
        request.session['raiz_etiquetado_auto'] = raiz
    else:
        request.session['raiz_preproceso'] = raiz


def obtener_carpeta_raiz(request, app=False):
    if app == 'indices':
        return request.session['raiz_indices']
    elif app == 'etiquetado':
        return request.session['raiz_etiquetado']
    elif app == 'etiquetado-auto':
        return request.session['raiz_etiquetado_auto']

    return request.session['raiz_preproceso']


def guardar_carpetas_seleccionadas(request, carpetas, app=False):
    if app == 'indices':
        request.session['carpetas_indices'] = carpetas
    elif app == 'etiquetado-auto':
        request.session['carpetas_etiquetado_auto'] = carpetas
    else:
        request.session['carpetas_preproceso'] = carpetas


def obtener_carpetas_seleccionadas(request, app=False):
    if app == 'indices':
        return request.session['carpetas_indices']

    return request.session['carpetas_preproceso']


def cambiar_diagonales_carpeta(carpeta):
    return carpeta.replace('\\', '/')


def guardar_ruta_csv_session(request, ruta_csv):
    request.session['csv_etiquetado'] = ruta_csv


def obtener_ruta_csv_session(request):
    return request.session['csv_etiquetado']


# def guardar_ruta_csv_session(request, ruta_csv, app=False):
#     if app == 'etiquetado':
#         request.session['csv_etiquetado'] = ruta_csv
#     elif app == 'etiquetado-auto':
#         request.session['csv_etiquetado_auto'] = ruta_csv


# def obtener_ruta_csv_session(request, app=False):
#     if app == 'etiquetado':
#         return request.session['csv_etiquetado']
#     elif app == 'etiquetado-auto':
#         return request.session['csv_etiquetado_auto']
