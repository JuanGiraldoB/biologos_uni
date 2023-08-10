from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TableData
import numpy as np
from .utils.Bioacustica_Completo import (
    Metodologia,
    ZscoreMV,
    lamda_unsup,
    segmentacion,
    seleccion_features,
    time_and_date,
    run_metodologia
)
import ast

from ecosonos.utils.session_utils import (
    save_selected_subfolders_session,
    save_root_folder_session,
    get_selected_subfolders_session,
    get_root_folder_session,
    save_csv_path_session,
    get_csv_path_session
)

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombres_base,
)

from ecosonos.utils.helper_functions import (
    get_percentage_advance
)

from .utils.helper_functions import (
    cargar_carpeta,
    procesar_carpetas,
    mostrar_tabla
)

from ecosonos.utils.archivos_utils import obtener_detalle_archivos_wav
from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import show_tkinter_windown_top
import asyncio
from asgiref.sync import sync_to_async


async def etiquetado_auto(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            return await cargar_carpeta(request)

        elif 'procesar_carpetas' in request.POST:
            return await procesar_carpetas(request)

        elif 'mostrar-tabla' in request.POST:
            return await mostrar_tabla(request)

    return render(request, "etiquetado_auto/etiquetado-auto.html")


@csrf_exempt
def barra_progreso(request):
    return get_percentage_advance()
