from django.shortcuts import render
from asgiref.sync import sync_to_async
from django.http import HttpResponse

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
from ecosonos.utils.archivos_utils import selecciono_archivo


from tkinter.filedialog import askdirectory, askopenfilename

import pandas as pd
from .plot_helper.plot import create_map
import json


def mapa(request):
    data = {}

    if 'cargar' in request.POST:
        root = mostrar_ventana_encima()
        archivo = askopenfilename(title='Seleccionar carpeta raiz')
        root.destroy()

        if selecciono_archivo(archivo):
            return render(request, 'conectividad/conectividad.html')

        with open('conectividad/static/conectividad/map_info.json') as f:
            departamentos = json.load(f)

        df_points = pd.read_excel(
            "C:\\Users\\JuanG\\Downloads\\UDAS_CSG_2018_JAGUAS.xlsx", sheet_name="Proyecto Piloto YNC")

        df_points = df_points[['latitude_IG', 'longitud_IG']]

        fig = create_map(departamentos, df_points)

        data['fig'] = fig

        return render(request, 'conectividad/conectividad.html', data)

    return render(request, 'conectividad/conectividad.html')
