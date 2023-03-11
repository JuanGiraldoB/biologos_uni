def inicializar_variables_session(request, ruta, grabaciones, n_grabaciones, PSD_medio):
    print("cargando archivos")
    request.session['ruta'] = ruta
    request.session['grabaciones'] = grabaciones
    request.session['n_grab'] = n_grabaciones
    request.session['index'] = 0

    request.session['PSD_medio'] = PSD_medio
    print('archivos cargados')


def guardar_raiz_carpeta_session(request, raiz, indices=False):
    if indices:
        request.session['raiz_indices'] = raiz
    else:
        request.session['raiz_preproceso'] = raiz


def guardar_grabaciones_session(request, archivos, indices=False):
    if indices:
        request.session['grabaciones_indices'] = archivos
    else:
        request.session['grabaciones_preproceso'] = archivos
