import soundfile as sf
from scipy import signal
from .calculo_indices import *
import pandas as pd
from tkinter.filedialog import askdirectory
from tqdm import tqdm
import numpy as np
from django.http import JsonResponse
import os
import plotly.express as px
# import matplotlib.pyplot as plt


def getRutasArchivos():
    """Obtiene las rutas de los archivos de audio con extension .WAV
    de la carpeta indicada por el usuario

    :return: Lista con las rutas de los archivos de audio con
    extension .WAV
    :rtype: list
    """

    rutas = []
    carpeta = askdirectory(title='Seleccionar carpeta con audios')
    archivos = os.listdir(carpeta)
    for archivo in archivos:
        # archivo = archivo.lower()
        # incluir los tipos de archivo de audio que soporta sf
        if archivo[-4:] == ".wav" or archivo[-4:] == ".WAV":
            rutas.append(carpeta + "/" + archivo)

    return rutas, carpeta


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


# G21A_20190520_190000.WAV
def csvIndices(indicesCalculados, ruta, indices_seleccionados):
    grabaciones = indicesCalculados[0]
    fechas = []
    horas = []

    for nombre in grabaciones:
        partes_nombre = nombre[:-4].split('_')
        fechas.append(partes_nombre[1])
        horas.append(partes_nombre[2])

    Valores = indicesCalculados

    data = None
    indices_seleccionados.insert(0, 'File')
    indicesDF = pd.DataFrame(data, columns=indices_seleccionados)

    for j in range(len(indices_seleccionados)):
        indicesDF[indices_seleccionados[j]] = Valores[j]

    indicesDF['fecha'] = fechas
    indicesDF['hora'] = horas

    nombreGrabacion = Valores[0][0]
    nombreGrabadora = nombreGrabacion.split('_')[0]
    indicesDF.to_csv(ruta + '/Indices_acusticos_' + nombreGrabadora +
                     '.csv', encoding='utf_8_sig', index=False, sep=',')


def calcularIndice(indices_seleccionados, carpeta, grabacion, Valores):
    """Calcula el valor de los indices seleccionados por el usuario.

    :param indices_seleccionados: Cadena de texto que agrupa las abreviaturas
    asociadas a los indices acusticos a calcular
    :type indices_seleccionados: string
    :return: Nombre y valor de los indices calculados
    :rtype: json
    """
    Indices_grabaciones = []

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
    for indice in indices_seleccionados:
        Indices_calculados[indice] = calcular_indices[indice]

    aux = []
    j = 0
    for indice in indices_seleccionados:
        j = j+1
        valor_indice = Indices_calculados[indice](parametros[indice])
        Valores[j].append(valor_indice)
        aux.append({"Name_indice": indice, "valor": valor_indice})

    Indices_grabaciones.append({"Grabacion": g, "Indices": list(aux)})

    # csvIndices(Valores, carpeta, indices_seleccionados)
    # graficaErrorBar(carpeta, grabaciones)
    # return carpeta, grabaciones
    # return JsonResponse({"Indices calculados": Indices_grabaciones})


def grafica_polar(carpeta_raiz, grabaciones, indice):
    # nombreGrabacion = grabaciones[0].split("/")[-1]
    # grabadora = nombreGrabacion.split('_')[0]

    if ".csv" in carpeta_raiz:
        df_all = pd.read_csv(carpeta_raiz)
    else:
        df_all = pd.read_csv(carpeta_raiz + '/indices_acusticos.csv')

    rdns = np.linspace(0, 360, 24, endpoint=False)

    df = df_all[['Date', indice]].copy()
    df['Dates'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d')
    df['Time'] = pd.to_datetime(df['Date']).dt.hour
    df['Hora'] = (df['Time'] / 24) * 360
    df.drop('Date', inplace=True, axis=1)
    df = df.groupby(['Dates', 'Time']).mean().reset_index()

    fig = px.bar_polar(df, r="Dates", theta="Hora",
                       color=indice, template="plotly_dark",
                       color_discrete_sequence=px.colors.sequential.Plasma_r)

    fig.update_layout(
        width=600,
        height=400,
        polar=dict(
            # hole=0.1,
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
                tickmode="array",
                tickvals=rdns,
                ticktext=["{}:00".format(int(h)) for h in range(24)],
                ticks="inside"
            ),
            radialaxis=dict(
                tickprefix='',
                ticksuffix='',
                showticklabels=False,
                range=(min(df['Dates'].unique()), max(df['Dates'].unique()))
            )
        )
    )

    fig = fig.to_html()
    return fig


def graficaErrorBar(ruta, grabaciones):
    nombreGrabacion = grabaciones[0].split("/")[-1]
    grabadora = nombreGrabacion.split('_')[0]
    df = pd.read_csv(ruta + '/Indices_acusticos_'+grabadora+'.csv')

    # Ignora las ultimas dos columnas(fecha y hora)
    normalized_df = df.iloc[:, :-2] / \
        df.iloc[:, :-2].max(axis=0, numeric_only=True)

    meanDF = normalized_df.mean(axis=0, numeric_only=True)
    stdDF = normalized_df.std(axis=0, numeric_only=True)

    mean_DF = meanDF.to_list()
    std_DF = stdDF.to_list()

    keys = meanDF.keys()

    x_pos = np.arange(len(keys.values))

    df_means = pd.DataFrame(
        {'Indices': meanDF.index, 'mean_DF': meanDF.values, 'std_DF': stdDF.values})

    return df_means


# def graficaErrorBar(ruta, grabaciones):
#     nombreGrabacion = grabaciones[0].split("/")[-1]
#     grabadora = nombreGrabacion.split('_')[0]
#     df = pd.read_csv(ruta + '/Indices_acusticos_'+grabadora+'.csv')
#     normalized_df = df / df.max(axis=0, numeric_only=True)

#     meanDF = normalized_df.mean(axis=0, numeric_only=True)
#     stdDF = normalized_df.std(axis=0, numeric_only=True)

#     mean_DF = meanDF.to_list()
#     std_DF = stdDF.to_list()

#     keys = meanDF.keys()

#     x_pos = np.arange(len(keys.values))

#     df_means = pd.DataFrame(
#         {'Indices': meanDF.index, 'mean_DF': meanDF.values, 'std_DF': stdDF.values})

#     return df_means

    # fig, ax = plt.subplots()
    # ax.bar(x_pos, mean_DF,
    #        yerr=std_DF,
    #        align='center',
    #        alpha=0.5,
    #        ecolor='black',
    #        capsize=10)

    # ax.set_xticks(x_pos)
    # ax.set_xticklabels(keys.values)
