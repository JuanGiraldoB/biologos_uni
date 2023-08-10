import pathlib
import os
import pandas as pd

from ecosonos.utils.archivos_utils import get_date_from_filename


def my_parser(archivos, dateformat='SM4', extension='.wav'):
    """
        Implementación personal del modulo 'parser' de maad,
        para ver el codigo original, dirigirse al modulo de
        maad.util y buscar la funcion 'parser'.
    """

    c_file = []
    c_date = []
    # find a file in subdirectories

    for archivo in archivos:
        print(f'archivo: {archivo}')
        if extension.upper() in archivo or extension.lower() in archivo:
            nombre_archivo = pathlib.Path(archivo)
            archivo_sin_extension = pathlib.Path(nombre_archivo).stem

            if '__' in archivo_sin_extension:
                archivo_sin_extension = archivo_sin_extension.replace(
                    '__', '_')

            c_file.append(archivo)
            c_date.append(get_date_from_filename(archivo_sin_extension))

    # SORTED BY DATE
    # create a Pandas dataframe with date as index
    df = pd.DataFrame({'file': c_file, 'Date': c_date})
    # define Date as index
    df.set_index('Date', inplace=True)
    # sort dataframe by date
    df = df.sort_index(axis=0)

    return df
