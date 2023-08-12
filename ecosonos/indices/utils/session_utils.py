def save_indices_session(request, selected_indices):
    request.session['indices_seleccionados'] = selected_indices


def get_indices_session(request):
    return request.session['indices_seleccionados']
