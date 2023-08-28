def save_root_folder_session(request, root, app='preproceso'):
    if app == 'indices':
        request.session['raiz_indices'] = root
    elif app == 'etiquetado':
        request.session['raiz_etiquetado'] = root
    elif app == 'etiquetado_auto':
        request.session['raiz_etiquetado_auto'] = root
    else:
        request.session['raiz_preproceso'] = root


def get_root_folder_session(request, app='preproceso'):
    if app == 'indices':
        return request.session['raiz_indices']
    elif app == 'etiquetado':
        return request.session['raiz_etiquetado']
    elif app == 'etiquetado_auto':
        return request.session['raiz_etiquetado_auto']

    return request.session['raiz_preproceso']


def save_selected_subfolders_session(request, subfolders, app='preproceso'):
    if app == 'indices':
        request.session['carpetas_indices'] = subfolders
    elif app == 'etiquetado_auto':
        request.session['carpetas_etiquetado_auto'] = subfolders
    else:
        request.session['carpetas_preproceso'] = subfolders


def get_selected_subfolders_session(request, app='preproceso'):
    if app == 'indices':
        return request.session['carpetas_indices']

    return request.session['carpetas_preproceso']


def save_csv_path_session(request, csv_path):
    request.session['csv_etiquetado'] = csv_path


def get_csv_path_session(request):
    return request.session['csv_etiquetado']


def save_subfolders_details_session(request, subfolder_details, app='preproceso'):
    if app == 'indices':
        request.session['detalle_archivos_indices'] = subfolder_details
    elif app == 'etiquetado_auto':
        request.session['detalle_archivos_etiquetado_auto'] = subfolder_details
    else:
        request.session['detalle_archivos_preproceso'] = subfolder_details


def get_subfolders_details_session(request, app='preproceso'):
    if app == 'indices':
        return request.session['detalle_archivos_indices']
    elif app == 'etiquetado_auto':
        return request.session['detalle_archivos_etiquetado_auto']
    else:
        return request.session['detalle_archivos_preproceso']


def get_files_session(request, app='preproceso'):
    if app == 'indices':
        return request.session['archivos_indices']
    elif app == 'etiquetado':
        return request.session['archivos_etiquetado']
    elif app == 'etiquetado_auto':
        return request.session['archivos_etiquetado_auto']
    else:
        return request.session['archivos_preproceso']


def save_files_session(request, files, app='preproceso'):
    if app == 'indices':
        request.session['archivos_indices'] = files
    elif app == 'etiquetado':
        request.session['archivos_etiquetado'] = files
    elif app == 'etiquetado_auto':
        request.session['archivos_etiquetado_auto'] = files
    else:
        request.session['archivos_preproceso'] = files


def save_statistics_state_session(request, statistics):
    request.session['statistics_preproceso'] = statistics


def get_statistics_state_session(request):
    return request.session['statistics_preproceso']


def save_destination_folder_session(request, destination_folder, app='preproceso'):
    if app == 'indices':
        request.session['destination_indices'] = destination_folder
    elif app == 'etiquetado_auto':
        request.session['destination_etiquetado_auto'] = destination_folder
    else:
        request.session['destination_preproceso'] = destination_folder


def get_destination_folder_session(request, app='preproceso'):
    if app == 'indices':
        return request.session['destination_indices']
    elif app == 'etiquetado_auto':
        return request.session['destination_etiquetado_auto']
    else:
        return request.session['destination_preproceso']
