from django.shortcuts import render
from asgiref.sync import sync_to_async
from django.http import HttpResponse

from ecosonos.utils.tkinter_utils import mostrar_ventana_encima
from tkinter.filedialog import askdirectory, askopenfilename

import pandas as pd
from .plot_helper.plot import create_map


def mapa(request):
    df_points = pd.read_excel(
        "C:\\Users\\JuanG\\Downloads\\UDAS_CSG_2018_JAGUAS.xlsx", sheet_name="Proyecto Piloto YNC")

    df_points = df_points[['latitude_IG', 'longitud_IG']]

    fig = create_map(df_points)

    return HttpResponse(fig)
