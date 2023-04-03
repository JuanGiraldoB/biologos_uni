# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import csv
import cv2
import os
import soundfile as sf
# from flask import Flask, jsonify
from scipy import signal
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
from csv import writer
import time


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


def play_sound(ruta, t_ini, t_fin):
    # Extract data and sampling rate from file
    data, fs = sf.read(ruta, dtype='float32')
    print('tamaño de la señal', data.shape)
    print('frecuencia de muestreo', fs)
    ini = min(int(t_ini*fs), int(t_fin*fs))
    fin = max(int(t_ini*fs), int(t_fin*fs))
    print(data[ini:fin].shape)
    sd.play(data[ini:fin], fs)
    status = sd.wait()

# como enviar la información de el tamaño de los vectores de tiempo y frecuencia
# además de la frecuencia de muestreo de la señal
# además del archivo que desea crear en csv?


def click_event(event, x, y, flags, params, img):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ' ', y)

        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(img, "{:.2f}".format((x/938)*60) + ' , ' +
                    "{:.2f}".format(24000-((y/513)*24000)), (x, y), font,
                    0.5, (255, 255, 255), 2)
        cv2.imshow('image', img)

        save_coordinates('CSV_file.csv', x, y)

    # if event == cv2.EVENT_RBUTTONDOWN:
    #    print(x, ' ', y)
    #    font = cv2.FONT_HERSHEY_SIMPLEX
    #    cv2.putText(img, "{:.2f}".format((x / 938) * 60) + ' , ' +
    #                "{:.2f}".format(24000 - ((y / 513) * 24000)), (x, y), font,
    #                0.8, (0, 0, 0), 2)

    #    cv2.imshow('image', img)
    #    save_coordinates(x,y)


def create_box(ruta, x1, y1, x2, y2):
    img = cv2.imread(ruta, 1)

    print(x1)
    pt1 = (int(x1), int(y1))
    pt2 = (int(x1), int(y2))
    pt3 = (int(x2), int(y1))
    pt4 = (int(x2), int(y2))
    color = (255, 255, 255)
    thickness = 1
    cv2.line(img, pt1, pt2, color, thickness)
    cv2.line(img, pt2, pt4, color, thickness)
    cv2.line(img, pt4, pt3, color, thickness)
    cv2.line(img, pt3, pt1, color, thickness)

    cv2.imwrite(ruta, img)


def coordinate_box(file, row1, row2):
    rows = []
    file = open(file)
    csvreader = csv.reader(file)
    for row in csvreader:
        rows.append(row)

    x1, y1 = rows[row1]
    x2, y2 = rows[row2]
    file.close()
    # remove_csvfile('CSVFILE.csv')
    return int(x1), int(y1), int(x2), int(y2)


def save_coordinates(filename, x, y):

    # The data assigned to the list
    data = [x, y]
    with open(filename, 'a', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(data)
        f_object.close()


def remove_csvfile(ruta):
    if os.path.isfile(ruta):
        os.remove(ruta)
        print("File has been deleted")
    else:
        print("File does not exist")


def create_csv(tempfile, filename):
    rows = []
    file = open(tempfile)
    csvreader = csv.reader(file)

    data = []
    for row in csvreader:

        x, y = row
        time = round((int(x) / 938) * 60, 2)
        frequency = round(24000 - ((int(y) / 513) * 24000), 2)

        # The data assigned to the list
        data.append([time, frequency])

    data_org = []

    for i in range(0, len(data)-1, 2):
        x1, y1 = data[i]
        x2, y2 = data[i+1]

        tmin = min(x1, x2)
        tmax = max(x1, x2)

        fmin = min(y1, y2)
        fmax = max(y1, y2)

        data_org.append([tmin, tmax, fmin, fmax])

    data_org = [["t_min", "t_max", "f_min", "f_max"]] + data_org

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writerows(data_org)
        file.close()


def run_spectogram(ruta):

    # ruta = 'C:/Users/lab_c/PycharmProjects/SpectrogramUtilities/Audios/G21A_20190520_190000.wav'
    ruta = './Audios/1.wav'

    f, t, s, audio, Fs = calcular_espectrograma(
        ruta
    )
# PENDIENTE######
    # Para reducir el tamaño de la imágen almacenada
    # como hacerlo automaticamente y que sirva con todo
    # tipo de señales
    s = s[:, ::3]
    # s = np.flipud(s)
    t = t[::3]
    print(s.shape)
    # for senal_audio in calcular_espectrograma(ruta):
    #    for Fs in calcular_espectrograma(ruta):
    # plt.specgram(senal_audio, Fs=fs, cmap='rainbow')
    plt.pcolormesh(s, shading='auto', cmap='cividis')
    # plt.xticks([])
    # plt.yticks([])
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')
    # plt.imsave('Spectrogram.png',s)
    plt.show()
    time.sleep(2)

    # s = s[:, ::3]
    # t = t[::3]

    # escoger los colormaps
    # plt.specgram(senal_audio, Fs=fs, cmap='rainbow')
    plt.pcolormesh(s, shading='auto', cmap='cividis')
    plt.imsave('Spectrogram.png', s, origin='lower', cmap='cividis')

    # plt.savefig('Spectrogram.png')

    # Que el biologo escoja la cantidad de eventos automaticamente
    max_event = 4
    row1 = 0
    row2 = 1
    file = 'CSV_file.csv'
    for i in range(max_event):
        img = cv2.imread('Spectrogram.png', 1)
        cv2.imshow('image', img)
        # que sean solamente dos eventos y no esperar la waitkey para dibujar las boxes
        cv2.setMouseCallback('image', click_event)
        cv2.waitKey(0)
        cv2.imwrite('Spectrogram.png', img)
        x1, y1, x2, y2 = coordinate_box(file, row1, row2)
        create_box('Spectrogram.png', x1, y1, x2, y2)
        play_sound(ruta, t[x1], t[x2])
        print("Coordenadas en tiempo: ["+"{:.2f}".format((t[int(x1)])) +
              " , "+"{:.2f}".format(t[int(x2)])+"]")
        print("Coordenadas en frecuencia: [" + "{:.2f}".format(24000-f[int(y1)]) +
              " , " + "{:.2f}".format(24000-f[int(y2)]) + "]")
        row1 = row1 + 2
        row2 = row2 + 2

    img = cv2.imread('Spectrogram.png', 1)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    time.sleep(2)
    # file.close(c)
    create_csv('CSV_file.csv', 'InfoSpectrogram.csv')
    remove_csvfile('CSV_file.csv')
    cv2.destroyAllWindows()

    # play_sound(ruta, t[int(x1)], t[int(x2)])
    # print("Coordenadas en tiempo: ["+"{:.2f}".format((t[int(x1)]))+" , "+"{:.2f}".format(t[int(x2)])+"]")
    # print("Coordenadas en frecuencia: [" + "{:.2f}".format(24000-f[int(y1)]) + " , " + "{:.2f}".format(24000-f[int(y2)]) + "]")
    # create_box('Spectrogram.png', x1, y1, x2, y2)
    # time.sleep(2)

    # convertir el csv final en tiempo frecuencia, no en par coordenado
    # Incluír ruta de la imagen para guardar
    # cambiar nombre del csv para que vean si se "etiquetan" dos quedan dos csv?


# if __name__ == "__main__":
#    app.run(debug=True, port=8000)
