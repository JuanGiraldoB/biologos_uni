import os


def obtener_subcarpetas(carpeta):
    carpetas_nombre_completo = []
    carpetas_nombre_base = []
    carpetas_nombre_completo.append(carpeta)
    carpetas_nombre_base.append(os.path.basename(carpeta))

    for ruta, carpetas_subdir, _ in os.walk(carpeta):
        # Add all directories to the carpetas list
        for carpeta_subdir in carpetas_subdir:
            nombre_completo = os.path.join(
                ruta, carpeta_subdir).replace('\\', '/')
            # os.path.join(ruta, carpeta_subdir).replace('\\', '/')
            carpetas_nombre_completo.append(nombre_completo)
            nombre_base = os.path.basename(os.path.join(ruta, carpeta_subdir))
            carpetas_nombre_base.append(nombre_base)
    return carpetas_nombre_completo, carpetas_nombre_base


def obtener_nombre_base(carpetas):
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


def guardar_ruta_xlsx_session(request, ruta_xlsx, app=False):
    if app == 'etiquetado':
        request.session['xlsx_etiquetado'] = ruta_xlsx
    elif app == 'etiquetado-auto':
        request.session['xlsx_etiquetado_auto'] = ruta_xlsx


def obtener_ruta_xlsx_session(request, app=False):
    if app == 'etiquetado':
        return request.session['xlsx_etiquetado']
    elif app == 'etiquetado-auto':
        return request.session['xlsx_etiquetado_auto']
