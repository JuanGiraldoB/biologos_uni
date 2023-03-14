import pandas as pd
import shutil


def mover_archivos_lluvia(carpeta_raiz, carpeta_destino):
    ruta_xlsx = f'{carpeta_raiz}/resultado.xlsx'
    xlsx_file = pd.read_excel(ruta_xlsx)

    for _, row in xlsx_file.iterrows():
        ruta_archivo = row['path_FI']
        lluvia = row['rain_FI']

        if lluvia == 'YES':
            shutil.move(ruta_archivo, carpeta_destino)
