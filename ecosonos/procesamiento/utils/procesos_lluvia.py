import os
import numpy as np
import soundfile as sf
import shutil
import sys
import time
import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
import tkinter.filedialog
from tkinter import ttk
# from flask import Flask, jsonify
from scipy import signal
# from Indices import *
import pandas as pd
from tqdm import tqdm
from scipy.stats.mstats import gmean


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


def algoritmo_lluvia(
    grabaciones, wn="hann", wl=1024, nfft=1024, ovlp=0, canal=2, cond=0
):
    """Esta función filtra las grabaciones con altos niveles de ruido,
    según la publicación [1], además se genera un umbral automático para el
    reconocimiento de las grabaciones más ruidosas.

    :param grabaciones: lista con las rutas de acceso a los archivos
    de audio con extension .WAV
    :type grabaciones: list
    :param wn: tipo de ventana, valor por defecto "hann"
    :type wn: str, optional
    :param wl: tamaño de la ventana, valor por defecto 512
    :type wl: int, optional
    :param nfft: número de puntos de la transformada de Fourier,
    valor por defecto, None, es decir el mismo de wl
    :type nfft: int, optional
    :param ovlp: puntos de solapamiento entre ventanas, valor por defecto 0
    :type ovlp: int, optional
    :param canal: valor entero asociado al canal de interes para grabaciones
    multicanal, valor por defecto, 2.
    :type canal: int, optional
    :param cond: valor entero que define si el calculo se realiza solo para
    las grabaciones consideradas buenas o si se etiquetan y se calcula para
    todas las grabaciones, valor por defecto, 0.
    :type cond: int, optional
    :return: Vector con el nombre de las grabaciones considerada buenas
    :rtype: numpy array
    :return: Vector con el nombre de las grabaciones considerada malas
    :rtype: numpy array
    """

    n_grabs = len(grabaciones)
    anotaciones = []
    banda_lluvia = (600, 1200)

    PSD_medio = np.zeros((n_grabs,))

    for i in tqdm(range(n_grabs)):

        # print("{} DE {}........ {:.2f} %".format(i,n_grabs,i/n_grabs*100))

        # try:
        x, Fs = sf.read(grabaciones[i])
        # except RuntimeError:
        #     return jsonify(
        #         {
        #             "Grabacion rechazada": grabaciones[i].split("/")[-1],
        #             "Motivo": "Archivo corrupto",
        #         }
        #     )
        # print(grabaciones[i])
        if len(x.shape) == 1:
            audio = x
        else:
            x = x.mean(axis=1)
            x = np.squeeze(x)
            audio = x

        puntos_minuto = Fs * 60

        npuntos = len(audio)
        banda = []

        for seg in range(0, npuntos, puntos_minuto):
            f, p = signal.welch(
                audio[seg: puntos_minuto + seg],
                Fs,
                nperseg=wl,
                window=wn,
                nfft=nfft,
                noverlap=ovlp,
            )
            banda.append(
                p[np.logical_and(f >= banda_lluvia[0], f <= banda_lluvia[1])])

        # try:
        banda = np.concatenate(banda)
        # except ValueError:
        #     return jsonify(
        #         {
        #             "Grabacion rechazada": grabaciones[i].split("/")[-1],
        #             "Motivo": "Archivo corrupto",
        #         }
        #     )

        PSD_medio[i] = np.mean(banda)

    PSD_medio = np.array(PSD_medio)
    PSD_medio_sin_ceros = PSD_medio[PSD_medio > 0]
    umbral = (
        np.mean(PSD_medio_sin_ceros) + gmean(PSD_medio_sin_ceros)
    ) / 2
    cond_buenas = np.logical_and(PSD_medio < umbral, PSD_medio != 0)
    cond_malas = np.logical_and(PSD_medio >= umbral, PSD_medio != 0)
    grabaciones = np.array(grabaciones)

    if cond == 1:
        grab_buenas = grabaciones
    else:
        grab_buenas = np.array(
            [grab.split("/")[-1] for grab in grabaciones[cond_buenas]]
        ).T

    grab_malas = np.array([grab.split("/")[-1]
                          for grab in grabaciones[cond_malas]]).T

    return grab_buenas, grab_malas, cond_malas


def csvReturn(ruta, grabaciones, condicion, request):

    grabacionesDf = pd.DataFrame()
    grabacionesDf = grabacionesDf.assign(File=None)
    grabacionesDf = grabacionesDf.assign(Status=None)
    n_grabs = len(grabaciones)

    archivos = []
    for i in range(n_grabs):
        archivos.append(grabaciones[i].split("/")[-1])
    grabacionesDf['File'] = archivos

    status = []
    for i in condicion:
        if i == True:
            status.append('Lluvia')
        else:
            status.append('Ok')
    nombreGrabacion = grabaciones[0].split("/")[-1]
    nombreGrabadora = nombreGrabacion.split('_')[0]
    grabacionesDf['Status'] = status

    # Guardar ruta en sesion para evitar abrir dialogos innecesarios?
    csv_ruta = f'{ruta}/Reporte_Lluvia_{nombreGrabadora}.csv'
    request.session['ruta_csv'] = csv_ruta

    grabacionesDf.to_csv(csv_ruta, index=False, sep=';')

    # grabacionesDf.to_csv('./procesamiento/csv/Reporte_Lluvia_' +
    #                      nombreGrabadora+'.csv', index=False, sep=';')


def removeRainFiles(ruta, ruta_csv):
    sourcePath = ruta
    receivePath = askdirectory(title='Carpeta de destino de audios con lluvia')
    # fileCSV = filedialog.askopenfile(
    #     title='Cargar archivo .csv con nombre de archivos y status de lluvia', mode='r')

    fileCSV = ruta_csv

    with open(fileCSV, 'r') as archivo:
        next(archivo, None)
        for line in archivo:
            line = line.rstrip()
            separator = ";"
            fileStatus = line.split(separator)

            if fileStatus[1] == 'Lluvia':
                shutil.move(sourcePath+'/'+fileStatus[0], receivePath)
