import os


def obtener_subcarpetas(carpeta):
    carpetas = []
    for ruta, carpetas_subdir, _ in os.walk(carpeta):
        # Add all directories to the carpetas list
        for carpeta_subdir in carpetas_subdir:
            carpetas.append(os.path.join(
                ruta, carpeta_subdir).replace('\\', '/'))
    return carpetas


def guardar_raiz_carpeta_session(request, raiz, indices=False):
    if indices:
        request.session['raiz_indices'] = raiz
    else:
        request.session['raiz_preproceso'] = raiz


def obtener_carpeta_raiz(request, indices=False):
    if indices:
        return request.session['raiz_indices']

    return request.session['raiz_preproceso']


def guardar_carpetas_seleccionadas(request, carpetas, indices=False):
    if indices:
        request.session['carpetas_indices'] = carpetas
    else:
        request.session['carpetas_preproceso'] = carpetas


def obtener_carpetas_seleccionadas(request, indices=False):
    if indices:
        return request.session['carpetas_indices']

    return request.session['carpetas_preproceso']
