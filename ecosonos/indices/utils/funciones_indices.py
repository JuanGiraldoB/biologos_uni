# from multiprocessing import Pool
# from procesamiento.models import Progreso
# from indices.models import Indices
from concurrent.futures import ThreadPoolExecutor, as_completed
import soundfile as sf
from scipy import signal
from .calculo_indices import *
import pandas as pd
from tkinter.filedialog import askdirectory
from tqdm import tqdm
import numpy as np
import asyncio
from ecosonos.utils.archivos_utils import get_date_from_filename, save_filename_in_txt
import pathlib
import os
import django
django.setup()

global stop_thread
stop_thread = False

# import matplotlib.pyplot as plt


def calcular_espectrograma(ruta):
    """Calcula el espectrograma del audio ubicado en la ruta
    y retorna valores de interes para el calculo de indices acusticos

    :param ruta: señal monoaural temporal
    :type ruta: string
    :return: Vector de frecuencia
    :rtype: numpy array
    :return: Vector de tiempo
    :rtype: numpy array
    :return: Vector de la señal de audio
    :rtype: numpy array
    :return: Frecuencia de muestreo
    :rtype: float
    """

    try:
        x, fs = sf.read(ruta)
    except RuntimeError:
        print("error en grabacion")

    if len(x.shape) == 1:
        senal_audio = x
    else:
        x = x.mean(axis=1)
        x = np.squeeze(x)
        senal_audio = x

    nmin = round(len(senal_audio) / (60 * fs))
    bio_band = (2000, 8000)
    tech_band = (200, 1500)
    wn = "hann"
    size_wn = 1024
    nmin = round(len(senal_audio) / (60 * fs))
    nperseg = nmin * size_wn
    noverlap = 0
    nfft = nmin * size_wn

    f, t, s = signal.spectrogram(
        senal_audio,
        fs=fs,
        window=wn,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
        detrend="constant",
        scaling="density",
        axis=-1,
        mode="magnitude",
    )

    return f, t, s, senal_audio, fs


def csvIndices(indicesCalculados, csv_path, indices_select):
    valores = indicesCalculados

    fechas = []

    for nombre in valores[0]:
        archivo_sin_extension = pathlib.Path(nombre).stem

        if '__' in archivo_sin_extension:
            archivo_sin_extension = archivo_sin_extension.replace(
                '__', '_')

        fechas.append(get_date_from_filename(archivo_sin_extension))

    valores.append(fechas)

    data = None
    indices_select.insert(0, 'File')
    indices_select.append('Date')
    indicesDF = pd.DataFrame(data, columns=indices_select)
    # pprint.pprint(indicesDF)

    try:

        for j in range(len(indices_select)):
            indicesDF[indices_select[j]] = valores[j]

        if 'ADIm' in indicesDF:
            for i in range(len(indicesDF['ADIm'][0])):
                indicesDF[f'ADIm_{i}'] = indicesDF['ADIm'].apply(
                    lambda x: x[i])

            indicesDF = indicesDF.drop(columns=['ADIm'])
    except Exception as e:
        print(e, " in adim")

    date_column = indicesDF.pop('Date')
    indicesDF['Date'] = date_column

    indicesDF.to_csv(csv_path,
                     encoding='utf_8_sig', index=False, sep=',')


def csvIndicesPool(valores, csv_path, indices_select):
    fechas = []
    for nombre in valores:
        archivo_sin_extension = pathlib.Path(nombre[0][0]).stem
        if '__' in archivo_sin_extension:
            archivo_sin_extension = archivo_sin_extension.replace(
                '__', '_')

        fechas.append(get_date_from_filename(archivo_sin_extension))

    # valores.append(fechas)

    data = None
    indices_select.insert(0, 'File')
    indices_select.append('Date')
    indicesDF = pd.DataFrame(data, columns=indices_select)

    try:

        for valor, date in zip(valores, fechas):
            # Create a new dictionary to store the row values
            row_values = {}

            # Iterate over each index and value in `valor`
            for j, value in enumerate(valor):
                column_name = indices_select[j]  # Get the column name
                # Assign the value to the corresponding column
                row_values[column_name] = value[0]

            row_values['Date'] = date

            # Append the row to the DataFrame
            indicesDF = indicesDF.append(row_values, ignore_index=True)

        if 'ADIm' in indicesDF:
            for i in range(len(indicesDF['ADIm'][0])):
                indicesDF[f'ADIm_{i}'] = indicesDF['ADIm'].apply(
                    lambda x: x[i])

            indicesDF = indicesDF.drop(columns=['ADIm'])
    except Exception as e:
        print(e)

    date_column = indicesDF.pop('Date')
    indicesDF['Date'] = date_column

    indicesDF.to_csv(csv_path,
                     encoding='utf_8_sig', index=False, sep=',')


async def run_calcular_indice(indices_select, archivos, csv_path, workers):
    global stop_thread
    stop_thread = False

    await asyncio.to_thread(calcular_indices_pool, indices_select, archivos, csv_path, workers)


def calcular_indices_pool(indices_select, archivos, csv_path, workers):
    from multiprocessing import Pool
    from procesamiento.models import Progreso
    from indices.models import Indices
    import time
    start_time = time.time()
    indices = Indices.objects.first()
    indices_select = indices.indices_seleccionados
    progreso = Progreso.objects.first()
    csv_path = indices.csv_path
    valores = []

    args_list = [(grabacion, indices_select, indices.valores)
                 for grabacion in archivos]

    total_tasks = len(args_list)
    completed_tasks = 0

    with Pool(processes=int(workers)) as pool:
        for result in pool.imap(process_grabacion_wrapper, args_list):
            valores.append(result)
            completed_tasks += 1

            global stop_thread
            if stop_thread:
                return

            # Update progress
            progreso.archivos_completados = completed_tasks
            progreso.save()

            print(f"Completed {completed_tasks}/{total_tasks} tasks")

    # with Pool(processes=10) as pool:
    #     valores = pool.starmap(process_grabacion, args_list)

    csvIndicesPool(valores, csv_path, indices_select)
    end_time = time.time()
    print(f"total time: {end_time-start_time}")


def process_grabacion_wrapper(args):
    return process_grabacion(*args)


def process_grabacion(grabacion, indices_select, valores):
    global stop_thread
    if stop_thread:
        return

    g = str(grabacion).split("/")[-1]
    valores[0].append(g)

    indices_calculados = {}
    f, t, s, audio, Fs = calcular_espectrograma(grabacion)
    parametros = {
        "ACIft": {"s": s},
        "ADI": {"s": s, "Fmax": 10000, "wband": 1000, "bn": -50},
        "ACItf": {"audio": audio, "Fs": Fs, "j": 5, "s": s},
        "BETA": {"s": s, "f": f, "bio_band": (2000, 8000)},
        "TE": {"audio": audio, "Fs": Fs},
        "ESM": {"s": s, "f": f, "fmin": 482, "fmax": 8820},
        "NDSI": {
            "s": s,
            "f": f,
            "bio_band": (2000, 8000),
            "tech_band": (200, 1500),
        },
        "P": {"s": s, "f": f, "bio_band": (2000, 8000), "tech_band": (200, 1500)},
        "M": {"audio": audio, "Fs": Fs, "depth": 16},
        "NP": {"s": s, "f": f, "nedges": 10},
        "MID": {"s": s, "f": f, "fmin": 450, "fmax": 3500},
        "BNF": {"s": s},
        "BNT": {"audio": audio, "fwin": 5},
        "MD": {
            "audio": audio,
            "Fs": Fs,
            "win": 256,
            "nfft": None,
            "type_win": "hann",
            "overlap": None,
        },
        "FM": {"s": s},
        "SF": {
            "audio": audio,
            "win": 256,
            "nfft": None,
            "type_win": "hann",
            "overlap": None,
        },
        "RMS": {"audio": audio},
        "CF": {"audio": audio},
        "SC": {"audio": audio, "Fs": Fs},
        "SB": {"audio": audio, "Fs": Fs},
        "Tonnets": {"audio": audio, "Fs": Fs},
        "SVE": {"s": s, "f": f, "fmin": 482, "fmax": 8820},
        "SNR": {"audio": audio, "axis": 0, "ddof": 0},
        "ADIm": {"s": s, "Fs": Fs, "wband": 1000},
    }

    calcular_indices = {
        "ACIft": ACIft,
        "ADI": ADI,
        "ACItf": ACItf,
        "BETA": beta,
        "TE": temporal_entropy,
        "ESM": spectral_maxima_entropy,
        "NDSI": NDSI,
        "P": rho,
        "M": median_envelope,
        "NP": number_of_peaks,
        "MID": mid_band_activity,
        "BNF": background_noise_freq,
        "BNT": background_noise_time,
        "MD": musicality_degree,
        "FM": frequency_modulation,
        "SF": wiener_entropy,
        "RMS": rms,
        "CF": crest_factor,
        "SC": spectral_centroid,
        "SB": spectral_bandwidth,
        "Tonnets": tonnetz,
        "SVE": spectral_variance_entropy,
        "SNR": signaltonoise,
        "ADIm": ADIm,
    }

    for indice in indices_select:
        indices_calculados[indice] = calcular_indices[indice]

    aux = []
    j = 0
    for indice in indices_select:
        j += 1
        valor_indice = indices_calculados[indice](parametros[indice])
        valores[j].append(valor_indice)
        aux.append({"Name_indice": indice, "valor": valor_indice})

    # progreso.archivos_completados += 1
    # progreso.save()

    save_filename_in_txt(grabacion)

    return valores


def calcular_indice(indices_select, archivos, csv_path, progreso):
    import time
    """Calcula el valor de los indices seleccionados por el usuario.

    :param indices_select: Cadena de texto que agrupa las abreviaturas
    asociadas a los indices acusticos a calcular
    :type indices_select: string
    :return: Nombre y valor de los indices calculados
    :rtype: json
    """
    start_time = time.time()

    global stop_thread
    indices_grabaciones = []

    grabaciones = archivos

    valores = list()
    for i in range(len(indices_select)+1):
        valores.append(list())

    for grabacion in tqdm(grabaciones):

        if stop_thread:
            return

        g = str(grabacion).split("/")[-1]
        valores[0].append(g)

        Indices_calculados = {}

        f, t, s, audio, Fs = calcular_espectrograma(
            grabacion
        )

        # Definicion de parametros para el calculo de indices acusticos
        parametros = {
            "ACIft": {"s": s},
            "ADI": {"s": s, "Fmax": 10000, "wband": 1000, "bn": -50},
            "ACItf": {"audio": audio, "Fs": Fs, "j": 5, "s": s},
            "BETA": {"s": s, "f": f, "bio_band": (2000, 8000)},
            "TE": {"audio": audio, "Fs": Fs},
            "ESM": {"s": s, "f": f, "fmin": 482, "fmax": 8820},
            "NDSI": {
                "s": s,
                "f": f,
                "bio_band": (2000, 8000),
                "tech_band": (200, 1500),
            },
            "P": {"s": s, "f": f, "bio_band": (2000, 8000), "tech_band": (200, 1500)},
            "M": {"audio": audio, "Fs": Fs, "depth": 16},
            "NP": {"s": s, "f": f, "nedges": 10},
            "MID": {"s": s, "f": f, "fmin": 450, "fmax": 3500},
            "BNF": {"s": s},
            "BNT": {"audio": audio, "fwin": 5},
            "MD": {
                "audio": audio,
                "Fs": Fs,
                "win": 256,
                "nfft": None,
                "type_win": "hann",
                "overlap": None,
            },
            "FM": {"s": s},
            "SF": {
                "audio": audio,
                "win": 256,
                "nfft": None,
                "type_win": "hann",
                "overlap": None,
            },
            "RMS": {"audio": audio},
            "CF": {"audio": audio},
            "SC": {"audio": audio, "Fs": Fs},
            "SB": {"audio": audio, "Fs": Fs},
            "Tonnets": {"audio": audio, "Fs": Fs},
            "SVE": {"s": s, "f": f, "fmin": 482, "fmax": 8820},
            "SNR": {"audio": audio, "axis": 0, "ddof": 0},
            "ADIm": {"s": s, "Fs": Fs, "wband": 1000},
        }

        calcular_indices = {
            "ACIft": ACIft,
            "ADI": ADI,
            "ACItf": ACItf,
            "BETA": beta,
            "TE": temporal_entropy,
            "ESM": spectral_maxima_entropy,
            "NDSI": NDSI,
            "P": rho,
            "M": median_envelope,
            "NP": number_of_peaks,
            "MID": mid_band_activity,
            "BNF": background_noise_freq,
            "BNT": background_noise_time,
            "MD": musicality_degree,
            "FM": frequency_modulation,
            "SF": wiener_entropy,
            "RMS": rms,
            "CF": crest_factor,
            "SC": spectral_centroid,
            "SB": spectral_bandwidth,
            "Tonnets": tonnetz,
            "SVE": spectral_variance_entropy,
            "SNR": signaltonoise,
            "ADIm": ADIm,
        }

        for indice in indices_select:
            Indices_calculados[indice] = calcular_indices[indice]

        aux = []
        j = 0
        for indice in indices_select:
            j = j+1
            valor_indice = Indices_calculados[indice](parametros[indice])
            valores[j].append(valor_indice)
            aux.append({"Name_indice": indice, "valor": valor_indice})

        progreso.archivos_completados += 1
        progreso.save()

        save_filename_in_txt(grabacion)

        indices_grabaciones.append({"Grabacion": g, "Indices": list(aux)})

    end_time = time.time()
    print(f"total time: {end_time-start_time}")

    csvIndices(valores, csv_path, indices_select)
    # graficaErrorBa, grabaciones)
    return grabaciones
    # return JsonResponse({"Indices calculados": Indices_grabaciones})


def stop_process_indices():
    global stop_thread
    stop_thread = True


def graficaErrorBar(ruta, grabaciones):
    nombreGrabacion = grabaciones[0].split("/")[-1]
    grabadora = nombreGrabacion.split('_')[0]
    df = pd.read_csv(ruta + '/Indices_acusticos_'+grabadora+'.csv')
    normalized_df = df / df.max(axis=0, numeric_only=True)

    meanDF = normalized_df.mean(axis=0, numeric_only=True)
    stdDF = normalized_df.std(axis=0, numeric_only=True)

    mean_DF = meanDF.to_list()
    std_DF = stdDF.to_list()

    keys = meanDF.keys()

    x_pos = np.arange(len(keys.values))

    df_means = pd.DataFrame(
        {'Indices': meanDF.index, 'mean_DF': meanDF.values, 'std_DF': stdDF.values})

    return df_means

    # fig, ax = plt.subplots()
    # ax.bar(x_pos, mean_DF,
    #        yerr=std_DF,
    #        align='center',
    #        alpha=0.5,
    #        ecolor='black',
    #        capsize=10)

    # ax.set_xticks(x_pos)
    # ax.set_xticklabels(keys.values)
