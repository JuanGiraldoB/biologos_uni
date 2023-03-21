def guardar_indices_session(request, indices_seleccionados):
    request.session['indices_seleccionados'] = indices_seleccionados


def obtener_indices_session(request):
    return request.session['indices_seleccionados']
