import os


def obtener_subcarpetas(carpeta):
    carpetas_nombre_completo = []
    carpetas_nombre_base = []
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


def guardar_raiz_carpeta_session(request, raiz, app=False):
    if app == 'indices':
        request.session['raiz_indices'] = raiz
    elif app == 'etiquetado':
        request.session['raiz_etiquetado'] = raiz
    else:
        request.session['raiz_preproceso'] = raiz


def obtener_carpeta_raiz(request, app=False):
    if app == 'indices':
        return request.session['raiz_indices']
    elif app == 'etiquetado':
        return request.session['raiz_etiquetado']

    return request.session['raiz_preproceso']


def guardar_carpetas_seleccionadas(request, carpetas, app=False):
    if app == 'indices':
        request.session['carpetas_indices'] = carpetas
    else:
        request.session['carpetas_preproceso'] = carpetas


def obtener_carpetas_seleccionadas(request, app=False):
    if app == 'indices':
        return request.session['carpetas_indices']

    return request.session['carpetas_preproceso']


def cambiar_diagonales_carpeta(carpeta):
    return carpeta.replace('\\', '/')
