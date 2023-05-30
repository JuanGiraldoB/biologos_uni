from django.shortcuts import render
from .utils.Bioacustica_Completo import (
    Metodologia,
    ZscoreMV,
    lamda_unsup,
    segmentacion,
    seleccion_features,
    time_and_date
)

from ecosonos.utils.carpeta_utils import (
    obtener_subcarpetas,
    guardar_carpetas_seleccionadas,
    guardar_raiz_carpeta_session,
    obtener_carpetas_seleccionadas,
    obtener_carpeta_raiz,
    selecciono_carpeta,
    subcarpetas_seleccionadas,
    obtener_nombre_base
)

from ecosonos.utils.archivos_utils import obtener_archivos_wav
from procesamiento.models import Progreso
import pandas as pd
from tkinter.filedialog import askdirectory
from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
import asyncio
from asgiref.sync import sync_to_async


async def etiquetado_auto(request):
    data = {}

    if request.method == 'POST':
        if 'cargar' in request.POST:
            root = mostrar_ventana_encima()
            carpeta_raiz = askdirectory(title='Seleccionar carpeta raiz')
            root.destroy()

            if selecciono_carpeta(carpeta_raiz):
                (request, "etiquetado_auto/etiquetado-auto.html")

            await sync_to_async(guardar_raiz_carpeta_session)(request, carpeta_raiz, app='etiquetado-auto')

            await sync_to_async(Progreso.objects.all().delete)()

            carpetas_nombre_completo, carpetas_nombre_base = await sync_to_async(obtener_subcarpetas)(carpeta_raiz)

            data['carpetas_nombre_completo'] = carpetas_nombre_completo
            data['carpetas_nombre_base'] = carpetas_nombre_base
            data['completo_base_zip'] = zip(
                carpetas_nombre_completo, carpetas_nombre_base)

            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

        elif 'procesar_carpetas' in request.POST:
            carpetas_seleccionadas = request.POST.getlist('carpetas')

            if subcarpetas_seleccionadas(carpetas_seleccionadas):
                return render(request, "etiquetado_auto/etiquetado-auto.html", data)

            await sync_to_async(guardar_carpetas_seleccionadas)(request, carpetas_seleccionadas,  app='etiquetado-auto')
            carpeta_raiz = await sync_to_async(obtener_carpeta_raiz)(request, app='etiquetado-auto')

            archivos_full_dir, archivos_nombre_base = await sync_to_async(obtener_archivos_wav)(carpetas_seleccionadas)

            print(len(archivos_full_dir))

            # progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(archivos))

            # asyncio.create_task(run_calcular_indices(
            #     carpeta_raiz, archivos, progreso))

            # await sync_to_async(calcular_indices)(carpeta_raiz, archivos, progreso)

            carpetas_seleccionadas = obtener_nombre_base(
                carpetas_seleccionadas)
            data['carpetas_procesando'] = carpetas_seleccionadas

            canal = 1
            autosel = 0
            visualize = 0
            banda = ["min", "max"]

            table, datos_clasifi, mean_class, infoZC, gadso, repre, dispersion, frecuencia = Metodologia(
                archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize)

            nombre_xlsx = 'Tabla_Nuevas_especies'

            for nombre in carpetas_seleccionadas:
                nombre_xlsx += f'_{nombre}'

            nombre_xlsx += '.xlsx'

            Tabla_NewSpecies = pd.DataFrame(table)
            Tabla_NewSpecies.to_excel(
                f'{carpeta_raiz}/{nombre_xlsx}', index=False)
            return render(request, "etiquetado_auto/etiquetado-auto.html", data)

    return render(request, "etiquetado_auto/etiquetado-auto.html")
