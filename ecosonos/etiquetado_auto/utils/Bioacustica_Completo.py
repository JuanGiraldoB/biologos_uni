from scipy.signal import savgol_filter
from scipy.signal import medfilt2d
import numpy as np
import skfuzzy as fuzz
import cv2
import numpy.matlib
from scipy import signal
import scipy
import soundfile as sf
import asyncio
import pandas as pd
import statistics as stat
from scipy.stats import zscore
from ecosonos.utils.archivos_utils import save_filename_in_txt

global stop_thread_metodologia, stop_thread_metodologia_prueba


def fcc5(canto, nfiltros, nc, nframes):
    """ Calculo de FCCs con escalamiento lineal
    Args:
        canto (array): Arreglo de entrada que contiene un segmento del espectro grama 
        nfiltros (escalar): Es un escalar de entrada (en la función segmentación lo toman como una constante = 14) empleado en filtro de canto
        nc (escalar): Es un escalar de entrada (en la función segmentación lo toman como una constante = 4) utilizada para evaluar la función dctm
        nframes (escalar): Es un escalar de entrada (en la función segmentación lo toman como una constante = 4) 

    Returns:
        y (array): Retorna caracteristicas FCCs  de canto"""
   # nfiltros = 14
    # nc = 4
    # nframes = 4
    # I11 = sio.loadmat('MCanto.mat')
    # canto = I11['canto']
    a, b = np.shape(canto)
    div = nframes
    w = int(np.floor(b/div))
    b1 = np.empty((a, 0), float)
    for k in range(0, w*div, w):
        bb = np.transpose(np.expand_dims(np.sum(np.power
                                                (np.abs(canto[:, k:k + w]), 2), axis=1), axis=0))
        b1 = np.append(b1, bb, axis=1)

    if a >= nfiltros:
        _h = np.zeros((nfiltros, a), np.double)
        wf = int(np.floor(a/nfiltros))
        h = np.empty((0, a), float)
        for k in range(0, wf*nfiltros, wf):
            hh = np.expand_dims(fuzz.gaussmf
                                (np.arange(a) + 1, k + wf, wf/4), axis=0)
            h = np.append(h, hh, axis=0)
    fbe = h@b1
    n = nc
    m = nfiltros

    def dctm(n, m): return np.multiply(np.sqrt(2/m),
                                       np.cos(np.multiply(np.matlib.repmat
                                                          (np.transpose(np.expand_dims
                                                                        (np.arange(n), axis=0)), 1, m),
                                                          np.matlib.repmat(np.expand_dims
                                                                           (np.multiply(np.pi, np.arange
                                                                                        (1, m + 1)-0.5)/m, axis=0), n, 1))))
    dct = dctm(n, m)
    y = dct@np.log(fbe)
    return y


def without_subband_mode_intensities(I1):
    """Reducción de ruido usando substracción espectral
    Args:
        I1 (array): Arreglo de entrada que contiene las amplitudes epectrales 
        filtrada con la función Gaussiana  

    Returns:
        I2 (array): Retorna la imagen I2 con la intensidad modal eliminada de cada subbanda.
    """
    M, N = np.shape(I1)
    I2 = np.zeros((M, N), np.double)
    mode1 = np.zeros((1, M), np.double)

    nf = 0
    for nf in range(0, M):
        thisi = I1[nf, :]
        thisi[thisi == np.inf] = np.nan

        maxi = np.max(np.real(thisi[:]))

        mini = np.min(np.real(thisi[:]))

        threshi = np.abs((mini-maxi)/2)

        hvec = np.arange(np.min(np.real(thisi[:])), np.max(np.real(thisi[:])))
        if np.size(hvec) == 1:
            hvec = np.expand_dims(np.linspace(mini, maxi, 2), axis=0)

        histii = np.object_(np.histogram(thisi[:], hvec))
        # histii,bins = np.histogram(thisi[:], hvec)
        # histii = np.real(histii)
        histi = histii[0]

        loc = np.argmax(histi[:])

        mode1_tmp = hvec[loc]
        mode1[0, nf] = mode1_tmp

    # Filtro de promedio Movil
    mode2 = savgol_filter(mode1, 11, 1)
    mode2 = np.transpose(mode2)

    for nf in range(0, M):
        I2[nf, :] = I1[nf, :]-mode2[nf]
    return I2


def findeccentricity(ellipse):
    secelip_1 = ellipse[1][0]
    secelip_2 = ellipse[1][1]
    if secelip_1 > secelip_2:
        elip_a = secelip_1
        elip_b = secelip_2
    else:
        elip_a = secelip_2
        elip_b = secelip_1

    elip_c = np.sqrt((elip_a**2)-(elip_b**2))
    eccentricity = elip_c/elip_a
    return eccentricity


def seg_xie(intensityi, specgram_time, specgram_frecuency):
    """Realiza en analisis de los elementos de mayor intensidad en el espectrograma para encontrar
    el tiempo y frecuencia maxima y minima de los elementos mas representativos del audio seleccionado

    Args:
        intensity (array): la variable spectrum, salida de la funcion specgram de matplotlib
        es una arreglo 2D que indica las intensidades sonoras del audio analizado.

        specgram_time (array): Es un arreglo de una dimension que indica el rango de tiempo que
        ocupa cada pixel en el espectrograma, es la salida "t" de la funcion specgram.

        specgram_frecuency (array): es un arreglo 1D que indica el rango de frecuencias que
        ocupa cada pixel en el spectrograma, es la salida "f" de la funcion specgram.


    Returns:
        segm_xie (array): Arreglo que pose el tiempo y frecuencia minima y maxima de cada
        elemento encontrado.
        Ejemplo: [tiempo_inicial,tiempo_final,frecuencia_inicial,frecuencia_final]

        segmentos_nor (array): Arreglo que pose la informacion de segm_xie, pero como
        posicion en el arreglo 2 otorgando el punto inicial y el ancho y alto del elemento.
        Ejemplo: [posicion_x,posicion_y,ancho,alto]
    """
    specgram_time = np.expand_dims(specgram_time, axis=0)
    specgram_frecuency = np.expand_dims(specgram_frecuency, axis=1)
    specgram_frecuency = np.flipud(specgram_frecuency)
    intensity = intensityi[1:, :]
    # funcion para pasar a desibelios.
    spectgram_intensity = 20 * (np.log10(np.abs(intensity)))
    gauss_intensity = cv2.GaussianBlur(spectgram_intensity, (13, 13), sigmaX=3,
                                       sigmaY=3)  # se utiliza un filtro gausiano.
    # modificar gaussian kernel
    try:
        with_suband = without_subband_mode_intensities(gauss_intensity)
    except Exception as e:
        print(e)

    with_suband = with_suband * (with_suband >= 0)
    # with_suband_normalizada = (with_suband -np.min(with_suband))/ (np.max(with_suband)-np.min(with_suband))

    # blancoNegro = np.round(255 * (with_suband_normalizada))
    # blancoNegro = blancoNegro.astype(int)
    # cv2.imwrite("seg_xie.png", blancoNegro)
    # guardo la imagen ya que no se puede manipular directamente.
    cv2.imwrite("seg_xie.png", with_suband)

    # la abro para pocerder con el programa, debo buscar una mejor solucion.
    with_suband = cv2.imread("seg_xie.png", 0)
    # with_suband=np.abs(with_suband)
    _, wsub_binarized = cv2.threshold(
        with_suband, 0, 255, type=(cv2.THRESH_BINARY + cv2.THRESH_OTSU))
    # se binariza con un filtro adaptativo y se invierte
    wsub_binarized = np.flipud(wsub_binarized)

    rectang_Kernel = cv2.getStructuringElement(cv2.MORPH_RECT,
                                               ksize=(9, 7))  # creo el kernel rectangular para la operacion de opening
    morf_opening = cv2.morphologyEx(
        wsub_binarized, cv2.MORPH_OPEN, rectang_Kernel, iterations=1)
    cuad_Kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, ksize=(6, 6))  # kernel para el Closening
    morf_close = cv2.morphologyEx(
        morf_opening, cv2.MORPH_CLOSE, cuad_Kernel, iterations=1)

    spectgram_contours, hierarchy = cv2.findContours(morf_close, cv2.RETR_TREE,
                                                     cv2.CHAIN_APPROX_SIMPLE)  # encuentro todos los grupos de pixeles blancos unidos
    spectgram_estructures = []

    # filtrando los contornos de acuerdo a su tamaño, area en bounding box y morfologia de la ecentricidad(si es circulo o linea)
    for cnt in spectgram_contours:
        # encontrando la bounding box del elemento
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)  # encontrando su area
        exent = area / (w * h)
        try:
            if area > 200 and area < 40000 and exent > 0.3:
                # me da los elemetos que componen una elipse
                ellipse = cv2.fitEllipse(cnt)
                eccentricity = findeccentricity(
                    ellipse)  # uso una funcion que cree para encontrar la exentricidad del elemento

                if eccentricity > 0.5:
                    spectgram_estructures.append(cnt)
            else:
                continue
        except:
            0

    segment = []  # Arreglo que pose el tiempo y frecuencia minima y maxima.
    segmentos_nor = []  # pose lo mismo que el anterior pero da la posicion en pixeles
    for element in spectgram_estructures:
        timeI, frecma, duration, magfrec = cv2.boundingRect(element)
        posicion = [int(timeI), int(frecma), int(duration), int(magfrec)]
        segment.append(
            [float(specgram_time[:, (posicion[0] + 1)]), float(specgram_time[:, (posicion[0] + posicion[2] - 1)]),
             float(specgram_frecuency[(posicion[1] + 1), :]),
             float(specgram_frecuency[(posicion[1] + posicion[3] - 1), :])])
        segmentos_nor.append(
            [posicion[0], posicion[1], posicion[2], posicion[3]])
    segm_xie = np.array(segment)
    segmentos_nor = np.array(segmentos_nor)

    return segm_xie, segmentos_nor


def time_and_date(archivos_full_dir, archivos_nombre_base):
    """
    Regresa una lista con las direcciones de cada audio en la carpeta seleccionada asi mismo la fecha
    y hora en la que fue tomado el audio y los devuelve como lista o como diccionario. 

    Args:
        dir (array): Direccion de la carpeta en la que se encuentran los audios a procesar. 

    Returns:
        fechas (array): Devuelve un arreglo en la que cada columna contiene la fecha
        y hora de un audio con el formato requerido.

        cronologia (array): Devuelve lo mismo que fechas pero en un diccionario.

        audios (array): Devuelve la direccion de cada audio encontrado en la carpeta seleccionada.

    """
    # nombres = os.listdir(archivos_full_dir)
    cronologia = {"nombre_archivo": [],
                  "Año": [], "Mes": [], "Dia": [],
                  "Hora": [], "Minuto": [], "Segundo": []}

    audios = []
    fechas = []

    for direccion, nombre in zip(archivos_full_dir, archivos_nombre_base):
        audios.append(direccion)
        if '__' in nombre:
            datos = nombre.split("__")
        else:
            datos = nombre.split("_")

        if len(datos) > 2:
            cronologia["nombre_archivo"].append(direccion)
            cronologia["Año"].append(datos[1][0:4])
            cronologia["Mes"].append(datos[1][4:6])
            cronologia["Dia"].append(datos[1][6:8])
            cronologia["Hora"].append(datos[2][0:2])
            cronologia["Minuto"].append(datos[2][2:4])
            cronologia["Segundo"].append(datos[2][4:6])

        elif len(datos) > 1:
            cronologia["nombre_archivo"].append(direccion)
            cronologia["Año"].append(datos[0][0:4])
            cronologia["Mes"].append(datos[0][4:6])
            cronologia["Dia"].append(datos[0][6:8])
            cronologia["Hora"].append(datos[1][0:2])
            cronologia["Minuto"].append(datos[1][2:4])
            cronologia["Segundo"].append(datos[1][4:6])

        else:
            cronologia["nombre_archivo"].append(direccion)
            cronologia["Año"].append("nan")
            cronologia["Mes"].append("nan")
            cronologia["Dia"].append("nan")
            cronologia["Hora"].append("nan")
            cronologia["Minuto"].append("nan")
            cronologia["Segundo"].append("nan")

    fechas.append(cronologia["nombre_archivo"])
    fechas.append(cronologia["Año"])
    fechas.append(cronologia["Mes"])
    fechas.append(cronologia["Dia"])
    fechas.append(cronologia["Hora"])
    fechas.append(cronologia["Minuto"])
    fechas.append(cronologia["Segundo"])
    fechas = np.array(fechas)

    return fechas, cronologia, audios


def ZscoreMV(datos_carac, zscore_min, rel_zscore):
    """calcula la desviacion estandar de la muestra

    Args:
        datos_carac (Array): Valores seleccionados de la matriz datos retornada por segmentacion
        zscore_min (array): el minimo valor en cada columna de datos_carac
        rel_zscore (array): la diferencia entre el valor maximo (zscore_max) y minimo
        (zscore_min) de cada columna de datos_carac

    Returns:
        out_zscore(array): resultado de la operacion.
    """
    num_datos, num_feat = datos_carac.shape[:2]
    meansc = np.matlib.repmat(zscore_min, num_datos, 1)
    varnsc = np.matlib.repmat(rel_zscore, num_datos, 1)
    out_zscore = (datos_carac-meansc)/(varnsc)
    return out_zscore


def segmentacion(archivos_full_dir, archivos_nombre_base, banda, canal, progreso):
    """Extrae los segmentos significativos en un rango de frecuencia presentes
    en los espectrogramas analizados de la carpeta seleccionada obteniendo
    sus nombres y frecuencia de muestreo.

    Args:
        ruta (str): Ubicacion de los archivos (carpeta)

        banda (list): Limite inferior y superior de las frecuencias buscadas
        de esta manera banda=[lim_inf,lim_sup]

        canal (int): canal en el que se realiza la operación

    Returns:
        segment_data (array): Informacion relevante de todos los segmentos detectados
        desde su posicion en tiempo, duracion, frecuencia, fecha de adquisicion etc.

        nombre_archivo (str array): Nombres de los archivos analizados.

        fs (int): frecuencia de muestreo
    """

    try:
        fechas, cronologia, audios = time_and_date(
            archivos_full_dir, archivos_nombre_base)
    except Exception as e:
        print('error 3 : ', e)

    ##### Funcion segmentacion########
    # esta se programa dentro de primer for con i = 1
    # se asume que el espectrograma genera los datos para s,f,t,p, los cuales son tomados de matlab
    # y1 = data['y']
    banda = np.array(banda)

    # p=0
    segment_data = []
    contador_archivos = -1
    nombre_archivo = []

    # Aqui se debe llamar la funcion del espectrograma.

    for archivo in audios:

        if stop_thread_metodologia or stop_thread_metodologia_prueba:
            print("Se ha detenido el proceso")
            return

        # if stop_thread_metodologia_prueba:
        #     return

        contador_archivos = contador_archivos + 1
        # leemos el audio
        try:
            x, fs = sf.read(archivo)
        except RuntimeError:
            print("error en grabacion: ", archivo)

        # Dependiendo del numero de canales lo promediamos
        if len(x.shape) == 1:
            senal_audio = x
        else:
            x = x.mean(axis=1)
            x = np.squeeze(x)
            senal_audio = x

        wn = "hann"
        size_wn = 1024
        noverlap = size_wn / 2
        nfft = size_wn * 2
        nmin = round(len(senal_audio) / (60 * fs))
        nperseg = nmin * size_wn

        frecuency, time, intensity = signal.spectrogram(senal_audio, fs=fs, window=wn, nfft=nfft, nperseg=nperseg,
                                                        noverlap=512, axis=-1, detrend=False, scaling="spectrum",
                                                        mode="psd")

        segm_xie_band = np.empty((0, 4), float)
        segmentos_nor_band = np.empty((0, 4), float)

        s = np.abs(intensity)
        u, v = np.shape(s)
        # resiz=len(y1[:,canal])/len(s[1,:])
        band_1 = 1 / u  # mirar si se usa para fmin
        band_2 = 1
        # intensity,frecuency,time,d=plt.specgram(senial[:,1],Fs=fs,NFFT=2048,noverlap=1550)

        mfband = medfilt2d(s, kernel_size=(5, 5))
        selband = np.flip(mfband, axis=0)

        # --------------------------  Xie ----------------------------------------
        if type(banda[1]) == np.str_:
            banda_aux = np.array([0, frecuency.max()])

        try:
            segm_xie, segmentos_nor = seg_xie(intensity, time, frecuency)
        except Exception as e:
            progreso.archivos_completados += 1
            progreso.save()

            save_filename_in_txt(archivo, "sonotipo", True)

            continue

        if len(segm_xie) > 0:
            for k in range(len(segm_xie[:, 1])):
                try:
                    ti = np.array(segm_xie[k, 0])  # tiempo inicial (X)
                    tf = np.array(segm_xie[k, 1])  # tiempo final(X+W)
                    fi = np.array(segm_xie[k, 3])  # frecuencia inicial (Y)
                    fff = np.array(segm_xie[k, 2])  # frecuencia final (Y+H)

                    if fi >= banda_aux[0] and fff <= banda_aux[1]:
                        segm_xie_band = np.append(segm_xie_band, np.expand_dims(
                            np.array([segm_xie[k, 0], segm_xie[k, 1], segm_xie[k, 2], segm_xie[k, 3]]), axis=0), axis=0)
                        segmentos_nor_band = np.append(segmentos_nor_band, np.expand_dims(
                            np.array([segmentos_nor[k, 0], segmentos_nor[k, 1],
                                      segmentos_nor[k, 2], segmentos_nor[k, 3]]),
                            axis=0), axis=0)
                except:
                    0

            segm_xie = segm_xie_band
            segmentos_nor = segmentos_nor_band

            k = 0
            for k in range(len(segm_xie[:, 1])):
                try:
                    ti = np.array(segm_xie[k, 0])  # tiempo inicial (X)
                    tf = np.array(segm_xie[k, 1])  # tiempo final(X+W)
                    fi = np.array(segm_xie[k, 3])  # frecuencia inicial (Y)
                    fff = np.array(segm_xie[k, 2])  # frecuencia final (Y+H)

                    x = np.array(segmentos_nor[k, 0]) + 1  # tiempo inicial (X)
                    xplusw = segmentos_nor[k, 0] + \
                        segmentos_nor[k, 2]  # Tiempo final(X+W)
                    y = segmentos_nor[k, 1] + 1  # frecuencia inicial (Y)
                    # frecuencia final (Y+H)
                    yplush = segmentos_nor[k, 1] + segmentos_nor[k, 3]
                    seg = np.array(
                        selband[int(y - 1):int(yplush), int(x - 1):int(xplusw)])
                    nfrec = 4
                    div = 4
                    nfiltros = 14  # se cambia porque con 30 se pierden muchos cantos
                    # 50 caracteristicas FCCs
                    features = fcc5(seg, nfiltros, div, nfrec)

                    fseg, cseg = np.shape(seg)
                    seg = ((seg - (np.matlib.repmat((np.min(np.real(seg[:]))), fseg, cseg)))
                           / ((np.matlib.repmat((np.max(np.real(seg[:]))), fseg, cseg))
                              - (np.matlib.repmat((np.min(np.real(seg[:]))), fseg, cseg))))

                    # cambio frecuencia dominante
                    sum_domin = np.transpose(
                        np.expand_dims(np.sum(seg, 1), axis=0))

                    dummy, dom = (np.max(np.real(np.transpose(np.expand_dims(savgol_filter(np.ravel(sum_domin), 1, 0), axis=0))))), np.argmax(
                        savgol_filter(np.ravel(sum_domin), 1, 0))

                    dom = ((((fi * u / (fs / 2)) + dom) / u)
                           * fs / 2)  # frecuencia dominante

                    dfcc = np.diff(features, 1)
                    dfcc2 = np.diff(features, 2)
                    cf = np.cov(features)
                    ff = []
                    for r in range(len(features[:, 0]) - 1):
                        ff = np.append(ff, np.diag(cf), axis=0)

                    # transforma la matriz en un vector tipo columna
                    features = np.expand_dims(
                        features.flatten(order='F'), axis=0)
                    # se agregan los resultados de dffcc y dffc2 a features
                    features = np.append(features, np.concatenate(
                        (np.expand_dims(np.mean(dfcc, 1), axis=0), np.expand_dims(np.mean(dfcc2, 1), axis=0)), axis=1),
                        axis=1)
                    features = np.transpose(features)

                    if tf > ti and fff > fi:

                        lista_aux1 = [
                            np.int16(fechas.T[contador_archivos, 2:6])]
                        lista_aux1 = np.array(lista_aux1)
                        lista_aux2 = np.concatenate(
                            (np.expand_dims(ti, axis=0), np.expand_dims(tf, axis=0), np.expand_dims(tf - ti, axis=0),
                             np.expand_dims(dom, axis=0), np.expand_dims(
                                fi, axis=0), np.expand_dims(fff, axis=0),
                             np.expand_dims(band_1, axis=0), np.expand_dims(band_2, axis=0)))
                        lista_aux2 = np.array(lista_aux2)
                        lista_aux3 = np.append(lista_aux1, lista_aux2)
                        lista_aux4 = np.append(lista_aux3, features.T)

                        segment_data.append(lista_aux4)
                        nombre_archivo.append(fechas[0, contador_archivos])
                    else:
                        0
                except:
                    0

        progreso.archivos_completados += 1
        progreso.save()

        save_filename_in_txt(archivo, "sonotipo")

    segment_data = np.array(segment_data)
    nombre_archivo = np.array(nombre_archivo)
    nombre_archivo = np.expand_dims(nombre_archivo, axis=1)

    return segment_data, nombre_archivo, fs


def mov_std(xmean, nueva_mean, n, std_p):
    """Calculo de desviación estándar móvil
    Args:
        xmean (vector): Vector de entrada tipo fila   
        nueva_mean (vector): Vector de entrada tipo fila  
        n(escalar): Es un escalar de entrada 
        std_p (vector): Vector de entrada tipo fila 

    Returns:
        nstd (vector): Vector de salida tipo fila 
    """
    a = (nueva_mean-xmean)**2
    b = (std_p**2)/n
    c = (a+b)*(n-1)
    nstd = c**(1/2)
    return nstd


def lamda_unsup(it_num, dat_norma):
    """LAMDA No supervisado - algoritmo de Clustering
    Args:
         it_num(escalar): Es un escalar de entrada que se manda desde la funcion metodologia como una constante=10.  
         dat_norma (array): Arreglo de entrada que contiene caracteristicas de clasificacion

    Returns:
        gadso (array): Arreglo de salida
        recon (vector): Vector de salida tipo fila  
        mean_clas (array): Arreglo de salida
        std_clas (array): Arreglo de salida
    """

    num_datos, num_feat = np.shape(dat_norma)
    num_clases = 1
    # Cluster prototypes initialized with the parameters of the first class (the no-information class (NIC))
    mean_clas = np.ones((1, num_feat))*0.5
    std_clas = np.ones((1, num_feat))*0.25
    conteo = np.array([0])

    for t in range(1, it_num+1):
        for j in range(0, num_datos):

            mjota = np.matlib.repmat((dat_norma[j, :]), num_clases, 1)
            mads = (mean_clas**(mjota))*((1-mean_clas)**(1-mjota))
            gads = np.prod(mads, axis=1) / \
                (np.prod(mads, axis=1)+(np.prod(1-mads, axis=1)))
            x, i_gad = (np.max(gads)), np.argmax(gads)

            if i_gad == 0:
                num_clases = num_clases + 1
                conteo = np.append(conteo, 1)
                mean_clas = np.append(mean_clas, np.expand_dims(
                    (np.mean(([mean_clas[0, :], dat_norma[j, :]]), axis=0)), axis=0), axis=0)
                reshh = mov_std(mean_clas[0, :], np.expand_dims(
                    (np.mean(([mean_clas[0, :], dat_norma[j, :]]), axis=0)), axis=0), 2, std_clas[0, :])
                std_clas = np.append(std_clas, reshh, axis=0)
            else:
                conteo[i_gad] = conteo[i_gad]+1
                new_mean = np.expand_dims(
                    mean_clas[i_gad, :] + (1/(conteo[i_gad]))*(dat_norma[j, :]-mean_clas[i_gad, :]), axis=0)
                std_clas[i_gad, :] = mov_std(
                    mean_clas[i_gad, :], new_mean, conteo[i_gad], std_clas[i_gad, :])
                mean_clas[i_gad, :] = new_mean
        perc = t*100/it_num
    gadso = np.zeros([num_clases, num_datos])  # consider the NIC
    # starts the assignment of data to the classes
    for j in range(0, num_datos):
        mjota = np.matlib.repmat((dat_norma[j, :]), num_clases, 1)
        mads = (mean_clas**(mjota))*((1-mean_clas)**(1-mjota))
        gadso[:, j] = np.prod(mads, axis=1) / \
            (np.prod(mads, axis=1)+(np.prod(1-mads, axis=1)))
    x, recon = np.expand_dims((np.max(gadso, axis=0)), axis=0), np.expand_dims(
        np.argmax(gadso, axis=0), axis=0)
    recon[0, 0] = 0
    a, b = np.shape(recon)
    for k in range(0, b):
        if x[0, k] < 0.8:
            # % tener en cuenta que los valores del GAD asignados a la NIC cuando se cumple este umbral, no tienen sentido.
            recon[0, k] = 0
    return gadso, recon, mean_clas, std_clas


def compute_icc(dat_norma, mean_clas, gadso):
    """Función para calcular la correlación intra clase
    Args:
         dat_norma (array): Arreglo de entrada que contiene caracteristicas de clasificacion
         mean_clas (array): Arreglo de entrada
         gadso (array): Arreglo de entrada
    Returns:
        icc (escalar): Escalar flotante  que contiene la correlacion intra clase
    """

    # data = sio.loadmat('PComputeICC.mat')
    # training_set = data['trainingSet']
    training_set = dat_norma
    magk = np.size(gadso, 0)
    magn = np.size(training_set, 0)
    sbe = []
    mke = np.zeros((np.size(gadso, 0), np.size(training_set, 1)))

    for c in range(0, magk):
        pre_mke = np.zeros((np.shape(training_set)))
        for n in range(0, magn):
            pre_mke[n, :] = numpy.matlib.repmat(
                gadso[c, n], 1, np.size(training_set, 1))*training_set[n, :]
        mke[c, :] = np.sum(pre_mke, axis=0)/np.sum(gadso[c, :])

    m = np.expand_dims(np.sum(training_set, axis=0)/magn, axis=0)
    pre_sbe = np.empty((0, magn), float)
    sbe = np.empty((0, magk), float)

    for c in range(0, magk):
        for n in range(0, magn):
            pre_sbe = np.append(
                pre_sbe, gadso[c, n]*np.dot((mke[c, :] - m), np.transpose(mke[c, :] - m)))
        sbe = np.append(sbe, np.sum(pre_sbe))
        pre_sbe = np.empty((0, magn), float)
    sbe = np.sum(sbe)
    dmin = np.min(scipy.spatial.distance.pdist(mean_clas))
    icc = (sbe/magn)*dmin*np.sqrt(magk)
    return icc


def compute_cv(mean_clas, gadso):
    """Función para calcular el coeficiente de variación
    Args:       
         mean_clas (array): Arreglo de entrada
         gadso (array): Arreglo de entrada
    Returns:
        cv (escalar): Escalar flotante  que contiene el coeficiente de variación
    """

    fila_gadso, columna_gadso = np.shape(gadso)
    pdis_max = np.zeros((0, columna_gadso))
    pdis_min = np.zeros((0, columna_gadso))
    c = 0
    z = (c+1)

    for c in range(0, fila_gadso-1):
        for z in range(c+1, fila_gadso):
            pdis_max1 = np.maximum(np.real(gadso[c, :]), np.real(gadso[z, :]))
            pdis_max = np.append(
                pdis_max, np.expand_dims(pdis_max1, axis=0), axis=0)

            pdis_min1 = np.minimum(np.real(gadso[c, :]), (gadso[z, :]))
            pdis_min = np.append(
                pdis_min, np.expand_dims(pdis_min1, axis=0), axis=0)

    dprima = 1-np.sum(pdis_min, 1)/np.sum(pdis_max, 1)
    dmin = np.min(dprima)
    dis = []
    dk = np.empty((fila_gadso, columna_gadso), float)
    umk = np.max(gadso, 1)
    for c in range(0, fila_gadso):
        for n in range(0, columna_gadso):
            dk[c, n] = umk[c]-gadso[c, n]
        dis = np.append(dis, np.expand_dims(
            1-np.sum(dk[c, :]*np.exp(dk[c, :]))/(columna_gadso*umk[c]*np.exp(umk[c])), axis=0), axis=0)

    dis = np.sum(dis)
    cv = (dis/columna_gadso)*dmin*np.sqrt(fila_gadso)
    return cv


def smooth(data):
    """Esta función  suaviza los datos en el vector  columna, 
    usando  un Filtro de promedio movil
    Args:       
         data (array): Arreglo de entrada al que se le desea aplicar el filtro
    Returns:
         moving_averages (array): Arreglo de salida que contiene la matriz filtrada
    """
    matriz = data
    if np.size(matriz) > 2:
        moving_averages = np.empty((0), float)
        for i in range(0, np.size(matriz)):
            if i == 0:
                moving_averages = np.append(moving_averages, matriz[i])
            elif i == 1:
                moving_averages = np.append(
                    moving_averages, (matriz[i-1] + matriz[i] + matriz[i+1])/3)
            elif (i >= 2) and (i <= (np.size(matriz)-3)):
                moving_averages = np.append(
                    moving_averages, (matriz[i-2] + matriz[i-1] + matriz[i] + matriz[i+1] + matriz[i+2])/5)
            elif (i == (np.size(matriz)-2)):
                moving_averages = np.append(
                    moving_averages, (matriz[i-1] + matriz[i] + matriz[i+1])/3)
            else:
                moving_averages = np.append(moving_averages, (matriz[i]))
    else:
        moving_averages = matriz
    return moving_averages


def seleccion_features(it_num, dat_norma):
    """Función para seleccionar características basado en correlación intra clase
       y coeficiente de variación
    Args:
         it_num(escalar): Es un escalar de entrada que se manda desde la funcion metodologia  
         dat_norma (array): Arreglo de entrada que contiene caracteristicas de clasificacion

    Returns:
        feat (array): Arreglo de salida tipo fila
        gadso (array): Arreglo de salida
        recon (vector): Vector de salida tipo fila  
        mean_clas (array): Arreglo de salida
        std_clas (array): Arreglo de salida
    """

    # data = sio.loadmat('Pseleccion_features')
    ex_level = 1
    # it_num=2
    # dat_norma = data['dat_norma']
    # mad = data['mad']
    # gad= data['gad']
    feat = []
    feat1 = []

    mcv = np.empty((0), float)
    micc = np.empty((0), float)
    gmcv = np.empty((np.size(dat_norma, 1), 0), float)
    gmicc = np.empty((np.size(dat_norma, 1), 0), float)
    maxfeat = np.size(dat_norma, 1)
    flag = 0
    j = 0
    k = 0

    for j in range(0, maxfeat):
        metric3 = np.empty((0), float)
        metric4 = np.empty((0), float)

        for k in range(0, np.size(dat_norma, 1)):
            if np.size(np.nonzero(k == np.array(feat))) == 0:
                gadso, recon, mean_clas, std_class = lamda_unsup(
                    it_num, dat_norma[:, feat+[k]])
                mean_clas = np.delete(mean_clas, 0, axis=0)
                std_class = np.delete(std_class, 0, axis=0)

                icc = compute_icc(dat_norma, mean_clas, gadso)
                cv = compute_cv(mean_clas, gadso)

                metric3 = np.append(metric3, icc)
                metric4 = np.append(metric4, cv)
            else:
                icc = 0
                cv = 0
                metric3 = np.append(metric3, icc)
                metric4 = np.append(metric4, cv)

        [dummy, ind] = np.max(metric4), np.argmax(metric4)
        mcv = np.append(mcv, dummy)
        micc = np.append(micc, metric3[ind])
        # se debe crear el vector con la mima dimension del vector que se desea concatenar
        # y esnecesario emplear expandim y axis=1
        gmcv = np.append(gmcv, np.expand_dims(metric4, axis=1), axis=1)
        gmicc = np.append(gmicc, np.expand_dims(metric3, axis=1), axis=1)
        feat = feat+[ind]
        # Filtro de promedio movil
        cr = smooth(smooth(mcv))
        cr = np.diff(cr)

        try:

            if np.sum([cr[-11:] < 0]) > 9:
                break

        except:
            print()
    [dummy, ind] = np.max(mcv), np.argmax(mcv)
    feat = feat[0:ind+1]

    [gadso, recon, mean_clas, std_class] = lamda_unsup(5, dat_norma[:, feat])
    feat = np.array(feat)
    feat = np.expand_dims(np.transpose(feat), axis=0)

    return feat, gadso, recon, mean_clas, std_class


async def run_metodologia(archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize, progreso, csv_name, metodologia_output):
    global stop_thread_metodologia, stop_thread_metodologia_prueba
    stop_thread_metodologia = False
    stop_thread_metodologia_prueba = False
    await asyncio.to_thread(Metodologia, archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize, progreso, csv_name, metodologia_output)


def Metodologia(archivos_full_dir, archivos_nombre_base, banda, canal, autosel, visualize, progreso, csv_name, metodologia_output):
    """Esta funcion genera la tabla con toda la informacion recopilada de los audios asi
    como una etiqueta para los audios con cierta similitud

    Args:
        ruta (str): Ruta de la carpeta con los audios a analizar
        banda (list): Limite inferior y superior de las frecuencias buscadas
        de esta manera banda=[lim_inf,lim_sup]
        canal (int): por defecto esta en 1
        autosel (int): elige entre el metodo de lamda o seleccion features
        visualize (int): no implementado aun, por defecto en 0

    Returns:
        table(array): Regresa una talba con todos los datos relevantes analizados
        datos_clasifi(array):Contiene los datos estadisticos realizados por zscore
        mean_class(array):Contiene los datos promedios de los segmentos, analizados
        por la funcion de Lamda
        infoZC(array): Contiene una seleccion especial de datos de los segmentos
        gadso(array): Seleecion de datos provenientes de la funcion lamda
        repre(array): pose los elementos representativos
        dispersion(array):pose la medida de dispersion o desviacion estandar de los
        elementos seleccionados, si habian mas de uno similar se suma.
        frecuencia(array): es un arreglo 3D que contiene el promedio y la desviacion 
        estandar de los datos seleccionados. 
    """

    canal = 1
    visualize = 0
    representativo = []
    frecuencia = []
    dispersion = []

    if type(banda[0]) == str and type(banda[1]) == str:
        datos, nombre_archivo, fs = segmentacion(
            archivos_full_dir, archivos_nombre_base, ["min", "max"], canal, progreso)
    else:
        datos, nombre_archivo, fs = segmentacion(
            archivos_full_dir, archivos_nombre_base, banda, canal, progreso)

    if visualize == 1:
        0
        # funcion que permite la visualizacion de los spectrogramas de cada audio
        # datos,nombre_archivo=VisualizacionSegs(rutain,datos,nombre_archivo,canal,banda)
    else:
        0

    if len(datos) > 0:
        datos_carac1 = np.array(datos[:, 7:10])
        datos_carac = np.zeros((datos_carac1.shape[0], 27))
        datos_carac2 = np.array(datos[:, 12:])

    try:
        datos_carac[:, 0:3] = datos_carac1
        datos_carac[:, 3:] = datos_carac2

        zscore_min = np.expand_dims(np.amin(datos_carac, axis=0), axis=0)
        zscore_max = np.expand_dims(np.amax(datos_carac, axis=0), axis=0)
        rel_zscore = zscore_max-zscore_min

        datos_clasifi = ZscoreMV(datos_carac, zscore_min, rel_zscore)

        infoZC = np.array([zscore_min, zscore_max, 0], dtype=object)
    except Exception as e:
        print(e)
    if autosel == 0:
        feat = np.array(list(range(0, len(datos_clasifi[1]))))
        infoZC[2] = np.expand_dims(feat, axis=0)
        gadso, recon, mean_class, std_class = lamda_unsup(2, datos_clasifi)
        mean_class = mean_class[1:, :]
        # elimina la primera fila por no ser relevantes
        std_class = std_class[1:, :]  # igual

        i = 0
        p = 0
        ind_eli = []
        sizeclasses = mean_class.shape[0]
        while p < sizeclasses:
            if sum(recon[0, :] == i) == 0:
                ind_eli.append(p)
                recon[recon > i] = recon[recon > i]-1
            else:
                i = i+1
            p = p+1
        mean_class = np.delete(mean_class, ind_eli, 0)
        gadso = np.delete(gadso, ind_eli, 0)

        for i in range(0, mean_class.shape[0]):
            ind_class = np.where(recon[0, :] == i)[0]

            euc = []
            for j in ind_class:
                vdat = mean_class[i, :]-datos_clasifi[j, :]
                euc.append(np.dot(vdat, vdat.T))
            [dummy, indm] = np.min(euc), np.argmax(euc)
            # indm siempe (o eso parece) siempre ser 1 tanto en python como en matlab, esto elige un indice
            # que de dejarse asi seria un error en python porque las listas comienzan en 0 y no en uno.
            representativo.append(ind_class[indm-1])
        mediafrecuencia = []
        stdfrecuencia = []

        for i in range(0, mean_class.shape[0]):
            indclass2 = np.where(recon[0, :] == i)[0]
            mediafrecuencia.append(np.mean(datos_carac[indclass2], axis=0))
            stdfrecuencia.append(np.std(datos_carac[indclass2], axis=0))

        frecuencia = np.array([mediafrecuencia, stdfrecuencia])
    else:
        feat, gadso, recon, mean_class, std_class = seleccion_features(
            2, datos_clasifi)
        mean_class = mean_class[1:, :]
        # elimina la primera fila por no ser relevantes
        std_class = std_class[1:, :]  # igual
        infoZC[2] = np.expand_dims(feat, axis=0)

        i = 0
        p = 0
        ind_eli = []
        sizeclasses = mean_class.shape[0]
        while p <= sizeclasses:
            if sum(recon[0, :] == i) == 0:
                ind_eli.append(p)
                recon[recon > i] = recon[recon > i]-1
            else:
                i = i+1
            p = p+1
        mean_class = np.delete(mean_class, ind_eli, 0)
        gadso = np.delete(gadso, ind_eli, 0)

        for i in range(0, mean_class.shape[0]):
            ind_class = np.where(recon[0, :] == i)[0]

            euc = []
            for j in ind_class:
                vdat = mean_class[i, :]-datos_clasifi[j, feat]
                euc.append(np.dot(vdat, vdat.T))
            [dummy, indm] = np.min(euc), np.argmax(euc)
            # indm siempe (o eso parece) siempre ser 1 tanto en python como en matlab, esto elige un indice
            # que de dejarse asi seria un error en python porque las listas comienzan en 0 y no en uno.
            representativo.append(ind_class[indm-1])
        mediafrecuencia = []
        stdfrecuencia = []

        for i in range(0, mean_class.shape[0]):
            indclass2 = np.where(recon[0, :] == i)[0]
            mediafrecuencia.append(np.mean(datos_carac[indclass2], axis=0))
            stdfrecuencia.append(np.std(datos_carac[indclass2], axis=0))

        frecuencia = np.array([mediafrecuencia, stdfrecuencia])
    salida = np.array(np.concatenate(
        [datos[:, 0:10], (fs/2)*(datos[:, 10:12])], axis=1))
    tarr = np.concatenate([salida, np.transpose(recon)], axis=1)

    table = np.concatenate([nombre_archivo, tarr], axis=1, dtype="object")

    prob = np.expand_dims((np.max(gadso, axis=0)), axis=1)

    table = np.concatenate([table, prob], axis=1, dtype="object")

    for i in range(0, np.max(recon)):
        dispersion.append(
            np.sum(np.std(datos_clasifi[(recon[0, :] == i), :], axis=1)))
    dispersion = np.expand_dims(np.array(dispersion), axis=0)

    column_mapping = {
        0: 'File',
        1: 'Month',
        2: 'Day',
        3: 'Hour',
        4: 'Minute',
        5: 'Start',
        6: 'End',
        7: 'Length',
        8: 'Fdom',
        9: 'FminVoc',
        10: 'FmaxVoc',
        11: 'Fmin',
        12: 'Fmax',
        13: 'Cluster',
        14: 'Membership'
    }

    import time
    # start time
    start_time = time.time()

    Tabla_NewSpecies = pd.DataFrame(table)
    Tabla_NewSpecies.rename(columns=column_mapping, inplace=True)
    Tabla_NewSpecies.to_csv(
        csv_name, index=False)

    try:
        metodologia_output.datos_clasifi = datos_clasifi.tolist()
        metodologia_output.mean_class = mean_class.tolist()
        infoZC = [arr.tolist() for arr in infoZC]
        metodologia_output.infoZC = infoZC
        metodologia_output.gadso = gadso.tolist()
        representativo = [int(item) for item in representativo]
        metodologia_output.representativo = representativo
        metodologia_output.dispersion = dispersion.tolist()
        metodologia_output.frecuencia = frecuencia.tolist()
        metodologia_output.save()
    except Exception as e:
        print(e)

    # end time
    end_time = time.time()
    # Calculate the execution time
    execution_time = end_time - start_time
    print(f"Time taken to save DataFrame to CSV: {execution_time} seconds")
    progreso.csv_cargado = True
    print(progreso.csv_cargado, "bioacustica")
    progreso.save()
    # request.session['table'] = table
    # print(request.session['table'])
    # return table, datos_clasifi, mean_class, infoZC, gadso, representativo, dispersion, frecuencia


def stop_process_metodologia():
    global stop_thread_metodologia
    stop_thread_metodologia = True


def stop_process_metodologia_prueba():
    global stop_thread_metodologia_prueba
    stop_thread_metodologia_prueba = True


def mlamda_fuzzy_3pi_apract(it_num, dat_norma, mean_class, flag):
    clusters, xx = np.shape(mean_class)
    num_clases, xx = np.shape(mean_class)
    num_datos, num_feat = np.shape(dat_norma)
    mean_class = np.append(
        (np.ones((1, num_feat), np.double))*0.5, mean_class, axis=0)
    conteo = np.zeros((1, 1000), np.double)  # hasta 1000 clases
    # winsorizacion prueba
    n, m = np.shape(dat_norma)

    if flag == 1:
        for t in range(1, it_num+1):

            for j in range(0, num_datos):

                mads = (mean_class**dat_norma[(j)*np.ones(np.size(mean_class, 0), dtype=int), :])*(
                    (1-mean_class)**(1-dat_norma[(j)*np.ones(np.size(mean_class, 0), dtype=int), :]))
                gads = np.prod(mads, axis=1) / \
                    (np.prod(mads, axis=1)+(np.prod(1-mads, axis=1)))
                x, i_gad = (np.max(gads)), np.argmax(gads)

                if i_gad == 0:
                    num_clases = num_clases + 1
                    conteo[0, num_clases-1] = 1
                    mean_class = np.append(mean_class, np.expand_dims(
                        (np.mean(([mean_class[0, :], dat_norma[j, :]]), axis=0)), axis=0), axis=0)

                else:
                    conteo[0, i_gad] = conteo[0, i_gad]+1
                    new_mean = np.expand_dims(
                        mean_class[i_gad, :] + (1/(conteo[0, i_gad]))*(dat_norma[j, :]-mean_class[i_gad, :]), axis=0)
                    mean_class[i_gad, :] = new_mean

        gadso = np.zeros([num_clases, num_datos])

        for j in range(0, num_datos):

            mads = (mean_class[1:, :]**dat_norma[(j)*np.ones(np.size(mean_class[1:, :], 0), dtype=int), :])*(
                (1-mean_class[1:, :])**(1-dat_norma[(j)*np.ones(np.size(mean_class[1:, :], 0), dtype=int), :]))
            gadso[:, j] = np.prod(
                mads, axis=1)/(np.prod(mads, axis=1)+(np.prod(1-mads, axis=1)))
        # delete(Bar)
        x, recon = np.expand_dims((np.max(gadso, axis=0)), axis=0), np.expand_dims(
            np.argmax(gadso, axis=0), axis=0)

    else:
        # %num_clases para retirar la NIC
        gadso = np.zeros([num_clases+1, num_datos])

        for j in range(0, num_datos):

            mads = (mean_class**dat_norma[(j)*np.ones(np.size(mean_class, 0), dtype=int), :])*(
                (1-mean_class)**(1-dat_norma[(j)*np.ones(np.size(mean_class, 0), dtype=int), :]))
            gadso[:, j] = np.prod(mads, axis=1) / \
                (np.prod(mads, axis=1)+np.prod(1-mads, axis=1))

        x, recon = np.expand_dims((np.max(gadso, axis=0)), axis=0), np.expand_dims(
            np.argmax(gadso, axis=0), axis=0)

    return gadso, recon, mean_class


async def run_metodologia_prueba(files_paths, files_basenames, banda, canal, specs, speciesStr, progreso, csv_path):
    global stop_thread_metodologia, stop_thread_metodologia_prueba
    stop_thread_metodologia = False
    stop_thread_metodologia_prueba = False
    await asyncio.to_thread(Metodologia_Prueba, files_paths, files_basenames, banda, canal, specs, speciesStr, progreso, csv_path)


def Metodologia_Prueba(files_paths, files_basenames, banda, canal, specs, speciesStr, progreso, csv_path):
    """Realiza las mismas acciones que metodologia pero esta se enfoca en buscar
    clusters ya existentes deacuerdo a los datos introducidos

    Args:
        ruta (str): Ruta donde estan los audios
        banda (list): lista de 2 valores de la frecuencia minima y maxima
        canal (int): canal a usar por defecto en 1
        specs (array): datos de los clusters a encontrar
        speciesStr (array): nombres de los los clusters a encontrar (primera fila de specs)

    Returns:
        table(array): Regresa una talba con todos los datos relevantes analizados
        pero con la clasificacion deacuerdo a los datos ingresados
        datos_clasifi(array):Contiene los datos estadisticos realizados por zscore
        mean_class(array):Contiene los datos promedios de los segmentos, analizados
        por la funcion de Lamda
        infoZC(array): Contiene una seleccion especial de datos de los segmentos
        gadso(array): Seleecion de datos provenientes de la funcion lamda
        repre(array): pose los elementos representativos
        dispersion(array):pose la medida de dispersion o desviacion estandar de los
        elementos seleccionados, si habian mas de uno similar se suma.
        frecuencia(array): es un arreglo 3D que contiene el promedio y la desviacion 
        estandar de los datos seleccionados. 
    """
    indnormal = []
    indmerged = []
    spec2SchInd = []
    for i in range(len(speciesStr)):
        for g in range(specs.shape[0]):
            if speciesStr[i] == specs[g, 0]:
                if len(specs[g, 0]) >= 7:
                    if specs[g, 0][0:7] == 'Merged_':
                        indmerged.append(g)
                    else:
                        indnormal.append(g)
                else:
                    indnormal.append(g)
                spec2SchInd.append(g)

    indmezclas = []
    mean_class = []
    mediafrecuencia = []
    stdfrecuencia = []

    for k in spec2SchInd:
        if k in indmerged:  # crep que nunca entra en este if, almenos en esta muestra
            params = specs[k][-1]
            for i in params:
                mean_class.append(i[0, :])
                mediafrecuencia.append(i[1, :])
                stdfrecuencia.append(i[2, :])
            indmezclas.append(specs[k][1].shape[0])
        else:
            params = specs[k][-1]
            mean_class.append(params[0, :])
            mediafrecuencia.append(params[1, :])
            stdfrecuencia.append(params[2, :])
            indmezclas.append(1)
    mean_class = np.array(mean_class)
    # e=mean_class
    feat = np.concatenate(specs[indnormal, 3])

    for j in indmerged:
        feat = np.concatenate(feat, specs[indmerged, 3])

    feat = np.unique(feat)

    a = np.concatenate(specs[indnormal, 4])

    for j in indmerged:
        a = np.concatenate(a, specs[indmerged, 4])

    b = np.concatenate(specs[indnormal, 5])

    for j in indmerged:
        b = np.concatenate(b, specs[indmerged, 5])

    mediafrecuencia = np.array(mediafrecuencia)
    stdfrecuencia = np.array(stdfrecuencia)

    if type(banda[0]) == str and type(banda[1]) == str:
        datos, nombre_archivo, fs = segmentacion(
            files_paths, files_basenames, ["min", "max"], canal, progreso)
    else:
        datos, nombre_archivo, fs = segmentacion(
            files_paths, files_basenames, banda, canal, progreso)

    try:
        # era desde 12 pero en los cambios de abril lo ponen en 13
        datos_carac = datos[:, 12:]
    except:
        print("No se encontraron vocalizaciones")
        table = []
        Fecha = []
        recon = []

    datos_carac1 = datos[:, 7:10]
    # datos_julian=datos[:,6:10] #De la actualizacion del codigo
    datos_carac2 = [datos_carac1, datos_carac]
    datos_carac = np.concatenate((datos_carac2), axis=1)

    blocal = np.amin(datos_carac, axis=0)
    alocal = np.amax(datos_carac, axis=0)

    aglobal = np.vstack((a, alocal))
    bglobal = np.vstack((b, blocal))
    aglobal = np.amax(aglobal, axis=0)
    bglobal = np.amin(bglobal, axis=0)
    aglobal = np.reshape(aglobal, (1, len(aglobal)))
    bglobal = np.reshape(bglobal, (1, len(bglobal)))

    datosnorm = ZscoreMV(datos_carac, bglobal, aglobal-bglobal)
    # aaa=datosnorm
    a1 = np.where(datosnorm > 1)
    b1 = np.where(datosnorm < 0)

    datosnorm[a1] = 1
    datosnorm[b1] = 0

    datos_clasifi = datosnorm

    infoZC = np.array([aglobal[0], bglobal[0], 0], dtype=object)

    for i in range(0, mean_class.shape[0]):
        mean_class[i, :] = (mean_class[i, :] * (a[i, :] -
                            b[i, :]) + b[i, :] - bglobal) / (aglobal - bglobal)

    feat = np.array(range(0, len(datos_clasifi[1])))
    infoZC[2] = feat
    datos_clasifi = datos_clasifi[:, :len(datos_clasifi[1])]

    mean_clas2 = []

    gadso, recon, mean_clas2 = mlamda_fuzzy_3pi_apract(
        10, datos_clasifi, mean_class, 0)
    meandom = mediafrecuencia[:, 0]
    stddom = stdfrecuencia[:, 0]
    datosdom = datos_carac[:, 0].T
    meandomt = np.resize(meandom, [1, meandom.shape[0]])
    stddomt = np.resize(stddom, [1, stddom.shape[0]])
    add = np.tile(datosdom, (meandom.shape[0], 1))
    bmd = np.tile(meandomt.T, (1, datosdom.shape[0]))
    csd = np.tile(stddomt.T, (1, datosdom.shape[0]))
    memberdom = np.exp(-(add-bmd)**2/(2*csd**2))

    Gadsdom = gadso[1:, :]
    threshold = np.exp((-(2*stddom)**2)/(2*stddom**2))
    thresholdt = np.resize(threshold, [1, stddom.shape[0]])
    Gadsdom[memberdom < np.tile(thresholdt.T, (1, memberdom.shape[1]))] = 0
    Gadsdom = np.vstack((gadso[0, :], Gadsdom))

    Indices = np.argsort(Gadsdom, axis=0)[::-1]
    recon = Indices[0, :]

    repre = np.zeros(mean_clas2.shape[0], dtype=int)
    for i in range(mean_clas2.shape[0]):
        Euc = np.zeros(datos_clasifi.shape[0])
        for j in range(datos_clasifi.shape[0]):
            V = mean_clas2[i, :] - datos_clasifi[j, :]
            Euc[j] = np.dot(V, V.T)
        repre[i] = np.argmin(Euc)

    mediafrecuencia2 = []
    stdfrecuencia2 = []

    for i in range(0, mean_clas2.shape[0]):
        indclass2 = np.where(recon == i)[0]
        mediafrecuencia2.append(np.mean(datos_carac[indclass2], axis=0))
        stdfrecuencia2.append(np.std(datos_carac[indclass2], axis=0))
    mediafrecuencia2 = np.array(mediafrecuencia2)
    stdfrecuencia2 = np.array(stdfrecuencia2)

    frecuencia = np.array([mediafrecuencia2, stdfrecuencia2])
    acc = 0
    aux_gadso = gadso[0, :]
    aux_mean_clas = mean_clas2[0, :]

    for i in range(len(indmerged)):
        mask = np.logical_and(indmerged[i] + acc >= recon, recon > acc)
        recon[np.where(mask)] = i + 1

        aux_gadso[i + 1, :] = np.max(gadso[acc +
                                     1:indmerged[i] + acc + 1, :], axis=0)
        aux_mean_clas[i + 1,
                      :] = np.mean(mean_clas2[acc + 1:indmerged[i] + acc + 1, :], axis=0)

        acc = indmerged[i] + acc

    gadso = aux_gadso
    mean_clas2 = aux_mean_clas
    salida = np.concatenate((datos[:, 0:10], datos[:, 10:12]*(fs/2)), axis=1)
    recon = np.reshape(recon, (len(recon), 1))
    tarr = np.concatenate((salida, recon), axis=1)
    table = np.concatenate((nombre_archivo, tarr), axis=1)
    Fecha = datos[:, 0:4]
    Dispersion = []

    gadso = gadso.reshape(-1, 1)

    try:
        prob = np.expand_dims((np.max(gadso, axis=1)), axis=1)
        table = np.concatenate([table, prob], axis=1, dtype="object")
    except Exception as e:
        print(e)

    for i in range(0, np.max(recon)+1):
        Dispersion.append(
            np.sum(np.std(datos_clasifi[np.where(recon == i)[0], :], axis=0)))
    Dispersion = (Dispersion - min(Dispersion)) / \
        (max(Dispersion) - min(Dispersion))

    column_mapping = {
        0: 'File',
        1: 'Month',
        2: 'Day',
        3: 'Hour',
        4: 'Minute',
        5: 'Start',
        6: 'End',
        7: 'Length',
        8: 'Fdom',
        9: 'FminVoc',
        10: 'FmaxVoc',
        11: 'Fmin',
        12: 'Fmax',
        13: 'Cluster',
        14: 'Membership'
    }

    Tabla_NewSpecies = pd.DataFrame(table)
    Tabla_NewSpecies.rename(columns=column_mapping, inplace=True)
    Tabla_NewSpecies.to_csv(
        csv_path, index=False)

    progreso.csv_cargado = True
    progreso.save()

    return table, datos_clasifi, mean_clas2, infoZC, gadso, repre, Dispersion, frecuencia


def guardado_cluster(nombre1, table, mean_class, infoZC, representativo, frecuencia):
    """Genera una fila por cada cluster encontrado en "table" que luego se usa para el
    reconocimiento de espeices. 
    Args:
        nombre1 (Str): Nombre provicional de los clusters, se repetira con una secuencia
        table (array): Tabla resultado de metodologia con la informacion resumen de todo
        mean_class(array): Informacion resultante de Metodologia
        infoZC (array): Informacion de resultante de Metodologia
        representativo (array): Vector que contiene los indices de table en los que estan
        los elementos representativos de cada cluster (se llama repre)
        frecuencia (array): informacion de las frecuencias resultante de metodologia.

    Returns:
        newSpec: Arreglo que contiene la informacion de los clusters seleccionados para entrenar
        el reconocimiento de esa especie, necesario para que "Metodologia_Prueba" identifique especies
    """
    newSpec = np.array([])
    for segmentos in range(0, int(max(table[:, -1]+1))):
        Nombre = nombre1+str(segmentos)
        seleccion = np.where(table[:, -1] == segmentos)
        elegidos = table[seleccion]
        fmin = np.mean(elegidos[:, 11])
        fmax = np.mean(elegidos[:, 12])
        clase = stat.mode(elegidos[:, -1])
        if segmentos >= len(representativo):
            print(
                f"Omitiendo el guardado del cluster {segmentos} ya que no pose la informacion necesaria")
            # print("Si aun decea crear el elemento faltante, agregue una fila adicional al representativo")
            # print(f"que ejemplifique el elemento a guardar (algun elemento del cluster {segmentos} puede ser adecudado)")
            # fila=seleccion[0]

            break
        else:
            fila = representativo[int(clase)]

        archivo = table[fila, 0]
        start = table[fila, 5]
        end = table[fila, 6]
        fv_min = table[fila, 9]  # frecuencia vocal minima
        fv_max = table[fila, 10]  # frecuencia vocal maxima

        classes = table[:, -1]
        names = np.unique(table[:, 0])
        addvector = np.zeros(classes.shape)

        for j in range(names.shape[0]):
            idx = [i for i, name in enumerate(table[:, 0]) if names[j] in name]

            ind = np.zeros(len(idx), dtype=int)
            for g in range(len(idx)):
                if np.isnan(idx[g]):
                    ind[g] = 0
                else:
                    ind[g] = 1
            ind = np.where(ind)[0]
            idx = np.array(idx)
            Selected = np.array(table[ind, 1:], dtype=float)

            for k in range(1, int(classes.max()) + 1):
                indclass = np.where(Selected[:, -1] == k)[0]
                Selectedclass = Selected[indclass, 4:6]
                I1 = np.lexsort((Selectedclass[:, 1], Selectedclass[:, 0]))
                Selectedclass = Selectedclass[I1]

                vectorl = np.zeros(Selectedclass.shape[0])
                for h in range(Selectedclass.shape[0]):
                    if h == Selectedclass.shape[0] - 1 and Selectedclass.shape[0] > 1:
                        outvect = zscore(vectorl[:-1])
                        vectorl[h] = np.mean(outvect)
                        # print(vectorl)
                    elif h == Selectedclass.shape[0] - 1:
                        vectorl[h] = 0
                    else:
                        vectorl[h] = Selectedclass[h + 1, 0] - \
                            Selectedclass[h, 1]

                addvector[idx[indclass]] = vectorl

        addvector[np.where(addvector < 0)] = 0

        repre = np.array([0, 0, 0, np.array([[start-1]]), np.array([[end+1]]), np.array([[fv_min-500]]),
                          np.array([[fv_max+500]]), np.array([[start]]
                                                             ), np.array([[fv_min]]), np.array([[end-start]]),
                          np.array([[fv_max-fv_min]]), np.array([[addvector[fila]]])], dtype=object)
        repre = np.reshape(repre, (1, 12))
        mediafrecuencia = frecuencia[0]
        stdfrecuencia = frecuencia[1]

        params = np.array([mean_class[int(clase), :], mediafrecuencia[int(
            clase), :], stdfrecuencia[int(clase), :]])

        newSpec_temp = np.array(
            [np.array([Nombre]), fmin, fmax, infoZC[2], infoZC[0], infoZC[1]], dtype=object)
        newSpec_temp[1] = np.array([[fmin]])
        newSpec_temp[2] = np.array([[fmax]])
        newSpec_temp = np.reshape(newSpec_temp, (1, 6))
        newSpec_temp = np.concatenate((newSpec_temp, repre), axis=1)

        newSpec0 = list(newSpec_temp)
        newSpec0 = newSpec0[0]
        newSpec0 = np.append(newSpec0, 0)
        newSpec0[18] = params
        newSpec0 = np.reshape(newSpec0, (1, 19))

        if newSpec.shape[0] <= 0:
            newSpec = newSpec0
        else:
            newSpec = np.concatenate((newSpec, newSpec0))
    return newSpec
