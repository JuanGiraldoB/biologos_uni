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

global stop_thread

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


def csvIndices(indicesCalculados, ruta, csv_path, indices_select):
    Valores = indicesCalculados

    fechas = []

    for nombre in Valores[0]:
        archivo_sin_extension = pathlib.Path(nombre).stem

        if '__' in archivo_sin_extension:
            archivo_sin_extension = archivo_sin_extension.replace(
                '__', '_')

        fechas.append(get_date_from_filename(archivo_sin_extension))
        # fecha, tiempo = nombre.split('_')[1:3]
        # tiempo = tiempo.split('.')[0]

        # dt_obj = datetime.datetime.strptime(
        #    fecha + tiempo, '%Y%m%d%H%M%S')

        # fechas.append(dt_obj)

    Valores.append(fechas)

    data = None
    indices_select.insert(0, 'File')
    indices_select.append('Date')
    indicesDF = pd.DataFrame(data, columns=indices_select)

    try:

        for j in range(len(indices_select)):
            indicesDF[indices_select[j]] = Valores[j]

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


async def run_calcular_indice(indices_select, carpeta, archivos, csv_path, progreso):
    global stop_thread
    stop_thread = False

    await asyncio.to_thread(calcular_indice, indices_select, carpeta, archivos, csv_path, progreso)


def calcular_indice(indices_select, carpeta, archivos, csv_path, progreso):
    global stop_thread
    import time
    # Start time
    start_time = time.time()
    """Calcula el valor de los indices seleccionados por el usuario.

    :param indices_select: Cadena de texto que agrupa las abreviaturas
    asociadas a los indices acusticos a calcular
    :type indices_select: string
    :return: Nombre y valor de los indices calculados
    :rtype: json
    """
    Indices_grabaciones = []

    grabaciones = archivos
    # carpeta = askdirectory(title='Seleccionar carpeta con audios')
    # archivos = os.listdir(carpeta)

    # for archivo in archivos:
    # archivo = archivo.lower()
    # incluir todos los formatos que queremos que soporte
    # if archivo[-4:] == ".wav" or archivo[-4:] == ".WAV":
    #     grabaciones.append(archivo)

    Valores = list()
    for i in range(len(indices_select)+1):
        Valores.append(list())

    for grabacion in tqdm(grabaciones):

        if stop_thread:
            return

        # TODO: OS SEP
        g = str(grabacion).split("/")[-1]
        Valores[0].append(g)

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
            Valores[j].append(valor_indice)
            aux.append({"Name_indice": indice, "valor": valor_indice})

        progreso.archivos_completados += 1
        progreso.save()

        save_filename_in_txt(grabacion)

        Indices_grabaciones.append({"Grabacion": g, "Indices": list(aux)})

    csvIndices(Valores, carpeta, csv_path, indices_select)
    # End time
    end_time = time.time()

    # Calculate the execution time
    execution_time = end_time - start_time
    print(f"Time taken: {execution_time} seconds")
    # graficaErrorBar(carpeta, grabaciones)
    return carpeta, grabaciones
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
