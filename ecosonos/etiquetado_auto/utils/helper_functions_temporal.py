from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import os
from django.conf import settings

from .plot_helper import (
    run_generate_hourly_pattern_graph_of_the_sonotype
)
from procesamiento.models import Progreso
import pandas as pd
from ecosonos.utils.tkinter_utils import get_file
import asyncio
from asgiref.sync import sync_to_async


async def process_hourly_sonotype(request):
    # Create an empty dictionary to store data that will be sent to the template
    data = {}
    try:
        # Get the CSV file path
        csv_path = await sync_to_async(get_file)()
    except Exception as e:
        print(e)
        return render(request, "etiquetado_auto/etiquetado_auto_temporal_ajax.html", data)

    # Check if there was a selected file and contains a ".csv" extension
    if not csv_path or ".csv" not in csv_path:
        return render(request, "etiquetado_auto/etiquetado_auto_temporal_ajax.html", data)

    dft = pd.read_csv(csv_path)
    unique_clusters = list(dft['Cluster'].unique())
    progreso = await sync_to_async(Progreso.objects.create)(cantidad_archivos=len(unique_clusters))
    asyncio.create_task(
        run_generate_hourly_pattern_graph_of_the_sonotype(dft, progreso))

    data['mostrar_barra_proceso'] = True
    return JsonResponse(data)
    # return render(request, "etiquetado_auto/etiquetado_auto.html", data)


def get_hourly_sonotype_plots_urls():
    img_dir = os.path.join(settings.BASE_DIR, 'etiquetado_auto', 'static',
                           'etiquetado_auto', 'img')

    # Get a list of image file names in the directory
    img_file_names = [f for f in os.listdir(
        img_dir) if f.lower().endswith(('.png'))]

    # Construct the URLs for each image
    img_urls = [os.path.join(
        settings.STATIC_URL, 'etiquetado_auto', 'img', fname) for fname in img_file_names]

    return JsonResponse({"img_urls": img_urls})
