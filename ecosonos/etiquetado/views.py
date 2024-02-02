from django.shortcuts import render

import os
from .utils.constants import REEMPLAZO

from .utils.spectograma import (
    play_segment,
)

from .utils.helper_functions import (
    load_folder,
    label_data,
    add_label,
    get_segment_data,
    prepare_destination_folder
)


def label_view(request):
    if request.method == 'POST':
        if 'cargar' in request.POST:
            return load_folder(request)
        elif 'destino' in request.POST:
            return prepare_destination_folder(request)

    return render(request, 'etiquetado/etiquetado.html')


def spectrogram_view(request, path):
    return label_data(request, path)


def play_segment_view(request, path):
    path = path.replace(REEMPLAZO, os.sep)

    segment_data = get_segment_data(request)
    add_label(request, path, segment_data)
    play_segment(path, segment_data['x0'], segment_data['x1'])

    return render(request, 'etiquetado/etiquetado.html')
