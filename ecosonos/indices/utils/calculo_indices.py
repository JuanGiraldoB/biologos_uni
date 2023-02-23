"""
Contiene los algoritmos que calculan cada uno de los posibles descriptores
de paisaje acústico.
Al usar referenciar como:
C. Isaza, D. Duque, S. Buritica and P. Caicedo. 
“Automatic identification of Landscape Transformation using acoustic 
recordings classification”,Ecological Informatics, 
ISSN: 15749541. SUBMITTED 2019.

Ultima modificacion - Documentacion, formato sphinx, formato de argumentos
Por: Cristian Camilo Acevedo
Diciembre 2021
"""

import math
import librosa
import numpy as np
from scipy import signal, stats


def ACItf(kwargs):
    """Calcula el indice de complejidad acústica original (ACI)
    primero sobre el tiempo y luego sobre la frecuencia
    [1] que fue renombrado en [2].
    Permite medir las variaciones de intensidad que se producen a lo
    largo de una grabación, en las distintas bandas de frecuencia.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: frecuencia de muestreo en Hz
    :type Fs: int
    :param j: tamaño de cada cluster en segundos
    :type j: int
    :param s: espectrograma de la señal
    :type s: numpy array
    :return: Valor del ACItf
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']
    j = kwargs['j']
    s = kwargs['s']

    # Para comparar grabaciones con diferente duración, hacer ACItf/t
    s = s / np.amax(s)
    specrows = s.shape[0]
    speccols = s.shape[1]

    dk = np.absolute(np.diff(s, axis=1))  # length speccols - 1

    # duracion de la grabación
    duracion = len(audio) / Fs
    m = math.ceil(duracion / j)  # Número de j en total
    n = math.floor(speccols / m)  # Número de tk en j

    ACI = np.zeros((specrows, m))

    for t in range(0, m):
        k1 = range(n * t, n * (t + 1) - 1)
        k2 = range(n * t, n * (t + 1))
        D = np.sum(dk[:, k1], axis=1)
        ACI[:, t] = np.divide(D, np.sum(s[:, k2], axis=1))

    ACI_dft = np.sum(ACI, axis=0)
    ACItot = sum(ACI_dft)

    return ACItot


def ACIft(kwargs):
    """Calcula el indice de complejidad acústica (ACIft)
    primero sobre la frecuencia y luego sobre el tiempo [2]
    Permite medir la información en dos bins de frecuencia sucesivos.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :return: Valor del ACIft
    :rtype: float
    """
    s = kwargs['s']

    s = s / np.amax(s)
    ACI = np.sum(np.divide(np.absolute(np.diff(s, axis=0)), s[1:, :] + s[:-1, :]))
    return ACI


def ADI(kwargs):
    """Calcula el índice de diversidad acústica (ADI) descrito en [3]
    Estima la diversidad de sonidos con la entropía de Shannon en franjas
    de frecuencia (bins) ADI se calcula con la ocupación de cada banda
    de frecuencia. La ocupación 𝑝𝑖 es la fracción del sonido en la banda i.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param Fmax: Frecuencia máxima para el análisis en Hz,
    valor por defecto 10000
    :type Fmax: int, optional
    :param wband: tamaño de cada banda de frecuencia en Hz,
    valor por defecto 1000
    :type wband: int, opcional
    :param bn: Valor del umbral (ruido de fondo) en dBFS,
    valor por defecto -50
    :type bn: int, opcional
    :return: Valor del ADI
    :rtype: float
    """

    s = kwargs['s']
    Fmax = kwargs['Fmax']
    wband = kwargs['wband']
    bn = kwargs['bn']

    s = s / np.amax(s)
    bn = 10 ** (bn / 20)
    sclean = s - bn
    sclean[sclean < 0] = 0
    sclean[sclean != 0] = 1
    nband = int(Fmax // wband)
    bin_step = int(s.shape[0] // nband)
    pbin = np.sum(sclean, axis=1) / s[:bin_step, :].size
    p = np.zeros(nband)

    for band in range(nband):
        p[band] = np.sum(pbin[band * bin_step : (band + 1) * bin_step]) + 0.0000001

    ADIv = -np.multiply(p, np.log(p))
    ADItot = np.sum(ADIv)

    return ADItot


def ADIm(kwargs):
    """Calcula el vector del índice de diversidad acústica modificado (ADIm)
    propuesto en [4]
    Se calcula ADI por bins de frecuencia de 1 kHz y el ruido de fondo
    de frecuencia utilizado es el del índice BNF reemplazando
    los -50 dB propuestos por el autor en ADI.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param Fs: Frecuencia de muestreo en Hz
    :type Fs: int
    :param wband: tamaño de cada banda de frecuencia en Hz,
    valor por defecto 1000
    :type wband: int, optional
    :return: Vector que contiene los valores del ADIm
    :rtype: numpy array
    """
    s = kwargs['s']
    Fs = kwargs['Fs']
    wband = kwargs['wband']


    bn = background_noise_freq_ADIm(s)
    # bn=-50
    # bn = 10**(bn/20)
    sclean = s - np.tile(bn, (s.shape[1], 1)).T
    sclean[sclean < 0] = 0
    sclean[sclean != 0] = 1
    Fmax = Fs / 2
    nband = int(Fmax // wband)
    bin_step = int(s.shape[0] // nband)
    pbin = np.sum(sclean, axis=1) / s[:bin_step, :].size
    p = np.zeros(nband)

    for band in range(nband):
        p[band] = np.sum(pbin[band * bin_step : (band + 1) * bin_step]) + 0.0000001

    ADIv = -np.multiply(p, np.log(p))
    ADIv = list(ADIv)

    return ADIv


def background_noise_freq(kwargs):
    """Calcula el valor del ruido de fondo para cada celda del
    espectrograma en el eje de las frecuencias (BNF) [5].

    :param s: Espectrograma de la señal
    :type s: numpy array
    :return: Vector que contiene el valor del ruido de fondo
    para cada celda de frecuencia
    :rtype: numpy array
    """
    s = kwargs['s']

    nfbins = s.shape[0]
    bn = np.zeros(nfbins)
    for i in range(nfbins):
        f = s[i, :]
        nbins = int(s.shape[1] / 8)
        H, bin_edges = np.histogram(f, bins=nbins)
        fwin = 5
        nbinsn = H.size - fwin
        sH = np.zeros(nbinsn)

        for j in range(nbinsn):
            sH[j] = H[j : j + fwin].sum() / fwin

        modep = sH.argmax()
        mode = np.amin(f) + (np.amax(f) - np.amin(f)) * (modep / nbins)

        acum = 0
        j = 0
        Hmax = np.amax(sH)
        while acum < 0.68 * Hmax:
            acum += H[j]
            j += 1

        nsd = np.amin(f) + (np.amax(f) - np.amin(f)) * (j / nbins)
        bn[i] = mode + 0.1 * nsd
        bnn = np.mean(bn)

    return bnn

def background_noise_freq_ADIm(s):
    """Calcula el valor del ruido de fondo para cada celda del
    espectrograma en el eje de las frecuencias (BNF) [5].

    :param s: Espectrograma de la señal
    :type s: numpy array
    :return: Vector que contiene el valor del ruido de fondo
    para cada celda de frecuencia
    :rtype: numpy array
    """

    nfbins = s.shape[0]
    bn = np.zeros(nfbins)
    for i in range(nfbins):
        f = s[i, :]
        nbins = int(s.shape[1] / 8)
        H, bin_edges = np.histogram(f, bins=nbins)
        fwin = 5
        nbinsn = H.size - fwin
        sH = np.zeros(nbinsn)

        for j in range(nbinsn):
            sH[j] = H[j : j + fwin].sum() / fwin

        modep = sH.argmax()
        mode = np.amin(f) + (np.amax(f) - np.amin(f)) * (modep / nbins)

        acum = 0
        j = 0
        Hmax = np.amax(sH)
        while acum < 0.68 * Hmax:
            acum += H[j]
            j += 1

        nsd = np.amin(f) + (np.amax(f) - np.amin(f)) * (j / nbins)
        bn[i] = mode + 0.1 * nsd
        bnn = np.mean(bn)

    return bnn


def background_noise_time(kwargs):
    """Calcula el valor del ruido de fondo de la señal en el tiempo
    (BNT) en dB [5]. Basado en el valor de modo de la señal de nivel
     de presión acústica inmediata (SPL)

    :param SPL: Señal con el nivel de presión sonora (SPL) de la señal en dB
    :type SPL: numpy array
    :param fwin: Tamaño de la ventana temporal para el análisis
    :type fwin: int
    :return: Valor de ruido de fondo en dB
    :rtype: float
    """
    audio = kwargs['audio']
    fwin = kwargs['fwin']
    SPL = wav2SPL(audio, -11, 9, 0.707)

    SPLmin = min(SPL)
    HdB, bin_edges = np.histogram(SPL, range=(SPLmin, SPLmin + 10))
    sHdB = np.zeros((len(HdB) - fwin, 1))

    for i in range(len(HdB) - fwin):
        sHdB[i] = sum(HdB[i : i + fwin] / fwin)

    modep = np.argmax(sHdB)
    bn = SPLmin + 0.1 * modep
    return bn


def beta(kwargs):
    """Calcula el índice bioacústico de la señal (β) [6]
    Mide la relación entre el ruido de fondo y las vocalizaciones de aves,
    basado en las observaciones de Boelman et al. (2007).
    Donde 𝛽𝐵 es la media del espectrograma a lo largo de la dimensión de tiempo.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param bio_band: tupla con la frecuencia mínima y máxima de la
    banda biofónica, valor por defecto: (2000, 8000)
    :type bio_band: tuple, optional
    :return: Valor de β
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    bio_band = kwargs['bio_band']

    minf = bio_band[0]
    maxf = bio_band[1]
    s = s / np.amax(s)
    s = 10 * np.log10(np.mean(s ** 2, axis=1))
    bioph = s[np.logical_and(f >= minf, f <= maxf)]
    bioph_norm = bioph - np.amin(bioph, axis=0)
    B = np.trapz(bioph_norm, f[np.logical_and(f >= minf, f <= maxf)])
    return B


def crest_factor(kwargs):
    """El factor de cresta (CF) es el cociente entre el valor pico de la
    señal de energía (Epeak) y su valor cuadrático medio (RMS).
    Los valores altos indican muchos picos en la señal de energía. [7]

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param rms: valor RMS de la señal
    :type rms: float
    :return: Valor para el factor de cresta de la señal
    :rtype: float
    """
    audio = kwargs['audio']
    rms = math.sqrt(sum(audio ** 2))

    audio2 = audio ** 2
    mint = max(audio2)
    cf = mint / rms
    return cf


def frequency_modulation(kwargs):
    """Calcula la modulación frecuencial (FM).
    FM es el ángulo medio de las derivadas direccionales.
    Los valores altos indican cambios abruptos en la intensidad.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :return: Valor de la modulación frecuencial
    :rtype: float
    """
    s = kwargs['s']

    ds_df = np.diff(s, axis=0)
    ds_dt = np.diff(s, axis=1)
    fm = np.mean(
        np.absolute(np.arctan(np.divide(-ds_df[:, 1:], -ds_dt[1:, :])))
        * (180 / math.pi)
    )

    return fm


def meanspec(kwargs):
    """[summary]

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: frecuencia de muestreo en Hz, valor por defecto 1
    :type Fs: int, optional
    :param wn: tipo de ventana, valor por defecto "hann"
    :type wn: str, optional
    :param ovlp: puntos de solapamiento entre ventanas, valor por defecto 0
    :type ovlp: int, optional
    :param wl: tamaño de la ventana, valor por defecto 512
    :type wl: int, optional
    :param nfft: número de puntos de la transformada de Fourier,
    valor por defecto, None, es decir el mismo de wl
    :type nfft: int, optional
    :param norm: booleano que indica si se normaliza o no el espectro,
    valor por defecto, True.
    :type norm: bool, optional
    :return: Vector con el espectro medio
    :rtype: numpy array
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']
    wn = kwargs['wn']
    ovlp = kwargs['ovlp']
    wl = kwargs['wl']
    nfft = kwargs['nfft']
    norm = kwargs['norm']

    f, t, Zxx = signal.stft(
        audio, fs=Fs, window=wn, noverlap=ovlp, nperseg=wl, nfft=nfft
    )
    mspec = np.mean(np.abs(Zxx), axis=1)

    if norm == True:
        mspec = mspec / max(mspec)

    return f, mspec


def median_envelope(kwargs):
    """Calcula la Media de la amplitud envolvente (M) [9].
    M da idea del tamaño de la señal.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: frecuencia de muestreo en Hz
    :type Fs: int
    :param depth: la profundidad de digitalización de la señal,
    valor por defecto 16
    :type depth: int, optional
    :return: valor de M
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']
    depth = kwargs['depth']

    min_points = Fs * 60
    npoints = len(audio)
    y = []
    VerParticion = npoints / min_points

    if VerParticion >= 3:
        for seg in range(min_points, npoints, min_points):
            y.append(np.abs(signal.hilbert(audio[seg - min_points : seg])))
    else:
        if VerParticion == 1:
            min_points = Fs * 20
        else:
            min_points = Fs * 30
        for seg in range(min_points, npoints, min_points):
            y.append(np.abs(signal.hilbert(audio[seg - min_points : seg])))

    y = np.concatenate([y])
    M = (2 ** (depth - 1)) * np.median(y)

    return M


def mid_band_activity(kwargs):
    """Calcula la  actividad acústica en la banda media (MID) [10]

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param fmin: frecuencia inferior de la banda media en Hz,
    valor por defecto 450
    :type fmin: int, optional
    :param fmax: frecuencia superior de la banda media en Hz,
    valor por defecto 3500
    :type fmax: int, optional
    :return: valor de la actividad acústica en la banda media
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    fmin = kwargs['fmin']
    fmax = kwargs['fmax']

    s = np.mean(s, axis=1)
    s = s ** 2
    s = s / np.amax(s)
    threshold = 10 * np.log10(np.mean(s))
    s = 10 * np.log10(s)
    MID = np.sum(s[np.logical_and(f >= fmin, f <= fmax)] > threshold) / len(s)

    return MID


def musicality_degree(kwargs):
    """Calcula el Grado de musicalidad (MD) mediante la pendiente media
    de la curva 1/f [11]. MD es una medida de la complejidad temporal de la señal.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: frecuencia de muestreo en Hz
    :type Fs: int
    :param win: tamaño de la ventana, valor por defecto 256
    :type win: int, optional
    :param nfft: número de puntos de la transformada de Fourier,
    valor por defecto, None, es decir el mismo de win
    :type nfft: [type], optional
    :param type_win: tipo de ventana, valor por defecto "hann"
    :type type_win: str, optional
    :param overlap: puntos de solapamiento entre ventanas,
    valor por defecto None, es decir win/2
    :type overlap: float, optional
    :return: Valor del grado de musicalidad
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']
    win = kwargs['win']
    nfft = kwargs['nfft']
    type_win = kwargs['type_win']
    overlap = kwargs['overlap']

    f, pxx = signal.welch(
        audio, Fs, nperseg=win, nfft=nfft, window=type_win, noverlap=overlap
    )
    f += 0.0000001
    lp2 = np.log10(pxx ** 2)
    lf = np.log10(f)
    dlf = np.diff(lf)
    dlp2 = np.diff(lp2)
    md_v = np.divide(dlp2, dlf)
    md = np.mean(md_v)

    return md


def NDSI(kwargs):
    """Calcula Índice de la diferencia normalizada de
    paisajes sonoros (NDSI).
    Estima el nivel de ruido antropogénico sobre el paisaje sonoro,
    mediante la relación entre el nivel de biofonía y tecnofonía.
    -1 indica biofonía pura y 1 indica pura tecnofonía.

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param bio_band: tupla con la frecuencia mínima y máxima
    de la banda biofónica, valor por defecto: (2000, 8000)
    :type bio_band: tuple, optional
    :param tech_band: tupla con la frecuencia mínima y máxima
    de la banda tecnofónica, valor por defecto: (200, 1500)
    :type tech_band: tuple, optional
    :return: Valor NDSI de la señal
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    bio_band = kwargs['bio_band']
    tech_band = kwargs['tech_band']

    s = np.mean(s, axis=1)
    s = s ** 2

    bio = s[np.logical_and(f >= bio_band[0], f <= bio_band[1])]
    B = np.trapz(bio, f[np.logical_and(f >= bio_band[0], f <= bio_band[1])])

    tech = s[np.logical_and(f >= tech_band[0], f <= tech_band[1])]
    A = np.trapz(tech, f[np.logical_and(f >= tech_band[0], f <= tech_band[1])])

    ND = (B - A) / (B + A)

    return ND


def number_of_peaks(kwargs):
    """Cuenta el número de picos en el espectro medio de la señal [13].
    Se estima el nivel de actividad acústica basado en el supuesto:
    "Entre más picos más actividad acústica".

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param nedges: número de partes en las que se divide la señal,
    por defecto 10
    :type nedges: int, optional
    :return: número de picos de la señal
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    nedges = kwargs['nedges']

    # Filtro de media móvil
    def smooth(a, n=10):
        """Esta función suaviza la señal con un filtro de media móvil.

        :param a: señal
        :type a: numpy array
        :param n: tamaño de la ventana del filtro de media móvil,
        por defecto 10
        :type n: int, optional
        :return: señal suavizada
        :rtype: numpy array
        """

        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1 :] / n

    s = np.sum(s, axis=1)
    s = s / np.amax(s)
    s = 20 * np.log10(s)
    s = smooth(smooth(s))  # suavizado de la señal
    f = smooth(smooth(f))
    s -= np.amin(s)
    ds = s[1:] - s[:-1]
    df = f[1:] - f[:-1]
    dsdf = np.divide(ds, df)

    step = round(len(s) / nedges)
    meansig = [np.mean(np.abs(s[j * step : (j + 1) * step])) for j in range(nedges)]

    ind = []

    if s[0] > meansig[0] and s[0] > 1.2 * np.mean(s) and np.mean(dsdf[1:4]) < 0:
        ind.append(0)

    for i in range(4, len(s) - 3):
        if (
            s[i] > meansig[i % nedges]
            and s[i] > 1.2 * np.mean(s)
            and np.mean(dsdf[i + 1 : i + 4]) > 0
            and np.mean(dsdf[i - 4 : i - 1]) < 0
        ):
            ind.append(i)

    if s[-1] > meansig[0] and s[-1] > 1.2 * np.mean(s) and np.mean(dsdf[-4:-1]) > 0:
        ind.append(len(s) - 1)

    if len(ind) == 0:
        NP = 0
        return NP

    NP = 1
    df_p = f[ind[1:]] - f[ind[:-1]]
    acum = 0

    for i in df_p:
        acum += i
        if acum >= 200:
            NP += 1
            acum = 0

    return NP


def rho(kwargs):
    """Calculo de la razón entre biofonía y tecnofonía (ρ) [14]

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param bio_band: tupla con la frecuencia mínima y máxima
    de la banda biofónica, valor por defecto: (2000, 8000)
    :type bio_band: tuple, optional
    :param tech_band: tupla con la frecuencia mínima y máxima
    de la banda tecnofónica, valor por defecto: (200, 1500)
    :type tech_band: tuple, optional
    :return: valor de ρ
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    bio_band = kwargs['bio_band']
    tech_band = kwargs['tech_band']

    s = np.mean(s, axis=1)
    s = s ** 2

    bio = s[np.logical_and(f >= bio_band[0], f <= bio_band[1])]
    B = np.trapz(bio, f[np.logical_and(f >= bio_band[0], f <= bio_band[1])])

    tech = s[np.logical_and(f >= tech_band[0], f <= tech_band[1])]
    A = np.trapz(tech, f[np.logical_and(f >= tech_band[0], f <= tech_band[1])])

    P = B / A

    return P


def rms(kwargs):
    """Calcula el valor de la raíz media cuadrática.
    Es una medida de amplitud de la señal.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :return: valor RMS
    :rtype: float
    """
    audio = kwargs['audio']

    erms = math.sqrt(sum(audio ** 2))
    return erms


def spectral_maxima_entropy(kwargs):
    """Calcula la entropía de los máximos espectrales (Hm) [10].

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param fmin: frecuencia inferior de la banda en la que se hará
    el análisis en Hz
    :type fmin: int
    :param fmax: frecuencia superior de la banda en la que se hará
    el análisis en Hz
    :type fmax: int
    :return: Valor del Hm
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    fmin = kwargs['fmin']
    fmax = kwargs['fmax']

    s = s / np.amax(s)
    s_max = np.max(s, axis=1)
    s_band = s_max[np.logical_and(f >= fmin, f >= fmax)]
    s_norm = s_band / np.sum(s_band)
    N = len(s_norm)
    Hm = -np.sum(np.multiply(s_norm, np.log2(s_norm))) / np.log2(N)

    return Hm


def spectral_variance_entropy(kwargs):
    """Calcula la entropía de la varianza espectral (Hv) [10].

    :param s: Espectrograma de la señal
    :type s: numpy array
    :param f: vector de frecuencias correspondientes al espectrograma s
    :type f: numpy array
    :param fmin: frecuencia inferior de la banda en la que se hará
    el análisis en Hz
    :type fmin: int
    :param fmax: frecuencia superior de la banda en la que se hará
    el análisis en Hz
    :type fmax: int
    :return: Valor del Hv
    :rtype: float
    """
    s = kwargs['s']
    f = kwargs['f']
    fmin = kwargs['fmin']
    fmax = kwargs['fmax']

    s = s / np.amax(s)
    s_std = np.std(s, axis=1)
    s_band = s_std[np.logical_and(f >= fmin, f >= fmax)]
    s_norm = s_band / np.sum(s_band)
    N = len(s_norm)
    Hv = -np.sum(np.multiply(s_norm, np.log2(s_norm))) / np.log2(N)

    return Hv


def temporal_entropy(kwargs):
    """Calcula la entropía acústica temporal (Ht) [15].

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: Frecuencia de muestreo en Hz
    :type Fs: int
    :return: Valor de Ht
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']

    min_points = Fs * 60
    npoints = len(audio)
    y = []
    VerParticion = npoints / min_points

    if VerParticion >= 3:
        for seg in range(min_points, npoints, min_points):
            y.append(np.abs(signal.hilbert(audio[seg - min_points : seg])))
    else:
        if VerParticion == 1:
            min_points = Fs * 20
        else:
            min_points = Fs * 30
        for seg in range(min_points, npoints, min_points):
            y.append(np.abs(signal.hilbert(audio[seg - min_points : seg])))

    env = np.concatenate([y])
    env_norm = env / np.sum(env)

    N = len(env_norm)
    Ht = -np.sum(np.multiply(env_norm, np.log2(env_norm))) / np.log2(N)
    return Ht


def wav2SPL(audio, sen, gain, Vrms):
    """Calcula el nivel de presión sonora de la señal [16].

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param sen: sensibilidad del micrófono en dB
    :type sen: float
    :param gain: ganancia del micrófono en dB
    :type gain: float
    :param Vrms: Voltaje RMS del conversor análogo digital de la grabadora
    :type Vrms: float
    :return: señal del nivel de presión sonora
    :rtype: numpy array
    """

    audio += 2 ** -17
    Vp = Vrms * math.sqrt(2)
    S = sen + gain + 20 * math.log10(1 / Vp)
    SPL = 20 * np.log10(np.absolute(audio)) - S
    return SPL


def wiener_entropy(kwargs):
    """Calcula la entropia de wiener o spectral flatness (SF) [17].
    Cuanto mayor sea el valor, más frecuencia complejidad.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param win: tamaño de la ventana, valor por defecto 256
    :type win: int, optional
    :param nfft: número de puntos de la transformada de Fourier,
    valor por defecto, None, es decir el mismo de win
    :type nfft: int, optional
    :param type_win: tipo de ventana, valor por defecto "hann"
    :type type_win: str, optional
    :param overlap: puntos de solapamiento entre ventanas,
    valor por defecto None, es decir win/2
    :type overlap: int, optional
    :return: valor de la entropia de wiener
    :rtype: float
    """
    audio = kwargs['audio']
    win = kwargs['win']
    nfft = kwargs['nfft']
    type_win = kwargs['type_win']
    overlap = kwargs['overlap']


    f, pxx = signal.welch(
        audio, nperseg=win, nfft=nfft, window=type_win, noverlap=overlap
    )
    num = stats.mstats.gmean(pxx)
    den = np.mean(pxx)
    spf = num / den
    return spf

def spectral_centroid(kwargs):
    """Calcula el centroide espectral

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: Frecuencia de muestreo en Hz
    :type Fs: int
    :return: valor del centroide espectral
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']

    SC = np.mean(librosa.feature.spectral_centroid(y=audio, sr=Fs))

    return SC

def spectral_bandwidth(kwargs):
    """Calcula el ancho de banda espectral

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: Frecuencia de muestreo en Hz
    :type Fs: int
    :return: valor del ancho de banda espectral
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']

    SB = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=Fs))
    
    return SB

def tonnetz(kwargs):
    """Calcula la red de tonos de la grabacion de audio

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param Fs: Frecuencia de muestreo en Hz
    :type Fs: int
    :return: valor de la red de tonos
    :rtype: float
    """
    audio = kwargs['audio']
    Fs = kwargs['Fs']
    
    ton = np.mean(librosa.feature.tonnetz(audio, Fs))
    
    return ton



# *********/*********/*********/*********/*********/*********/*********/**
def signaltonoise(kwargs):
    """Calcula la relación señal a ruido (SNR)
    La diferencia entre el valor máximo en dB y el valor en dB de BGN,
    entre mayor sea el valor la señal tiene menos ruido.

    :param audio: señal monoaural temporal
    :type audio: numpy array
    :param axis: Si el eje es igual a Ninguno, la matriz se desdobla primero,
    valor predeterminado = 0
    :type axis: int, optional
    :param ddof: Corrección de los grados de libertad para la desviación
    estándar. El valor predeterminado = 0.
    :type ddof: int, optional
    :return: Valor de SNR
    :rtype: float
    """
    audio = kwargs['audio']
    axis = kwargs['axis']
    ddof = kwargs['ddof']

    mx = np.amax(audio)
    a = np.divide(audio, mx)
    a = np.square(a)
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis)
    snr = np.where(sd == 0, 0, m / sd)
    snr = float(snr)

    return snr


"""

    Referencias:

    [1] Pieretti, N., Farina, A., & Morri, D. (2011). A new methodology to infer the singing activity of an avian
        community: The Acoustic Complexity Index (ACI). Ecological Indicators, 11(3), 868–873.
        http://doi.org/10.1016/j.ecolind.2010.11.005

    [2] Farina, A., Pieretti, N., Salutari, P., Tognari, E., & Lombardi, A. (2016). The Application of the Acoustic
        Complexity Indices (ACI) to Ecoacoustic Event Detection and Identification (EEDI) Modeling. Biosemiotics, 9(2),
        227–246. http://doi.org/10.1007/s12304-016-9266-3

    [3] Pekin, B. K., Jung, J., Villanueva-Rivera, L. J., Pijanowski, B. C., & Ahumada, J. A. (2012). Modeling acoustic
        diversity using soundscape recordings and LIDAR-derived metrics of vertical forest structure in a neotropical
        rainforest. Landscape Ecology, 27(10), 1513–1522. http://doi.org/10.1007/s10980-012-9806-4

    [4] Duque-Montoya, D. C. (2018). Methodology for Ecosystem Change Assessing using Ecoacoustics Analysis.
        Universidad de Antioquia.

    [5] Towsey, M. (2013). Noise removal from waveforms and spectrograms derived from natural recordings of the
        environment. Retrieved from http://eprints.qut.edu.au/61399/

    [6] Boelman, N. T., Asner, G. P., Hart, P. J., & Martin, R. E. (2007). Multi-trophic invasion resistance in Hawaii:
        Bioacoustics, field surveys, and airborne remote sensing. Ecological Applications, 17(8), 2137–2144.
        http://doi.org/10.1890/07-0004.1

    [7] Torija, A. J., Ruiz, D. P., & Ramos-Ridao, a F. (2013). Application of a methodology for categorizing and
        differentiating urban soundscapes using acoustical descriptors and semantic-differential attributes.
        The Journal of the Acoustical Society of America, 134(1), 791–802. http://doi.org/10.1121/1.4807804

    [8] Tchernichovski, O., Nottebohm, F., Ho, C., Pesaran, B., & Mitra, P. (2000). A procedure for an automated
        measurement of song similarity. Animal Behaviour, 59(6), 1167–1176. http://doi.org/10.1006/anbe.1999.1416

    [9] Depraetere, M., Pavoine, S., Jiguet, F., Gasc, A., Duvail, S., & Sueur, J. (2012). Monitoring animal diversity
        using acoustic indices: Implementation in a temperate woodland. Ecological Indicators, 13(1), 46–54.
        http://doi.org/10.1016/j.ecolind.2011.05.006

    [10] Towsey, M., Wimmer, J., Williamson, I., & Roe, P. (2014). The use of acoustic indices to determine avian
        species richness in audio-recordings of the environment. Ecological Informatics, 21, 110–119.
        http://doi.org/10.1016/j.ecoinf.2013.11.007

    [11] De Coensel, B., Botteldooren, D., Debacq, K., Nilsson, M. E., & Berglund, B. (2007).
        Soundscape classifying ants. In Internoise. http://doi.org/10.1260/135101007781447993

    [12] Kasten, E. P., Gage, S. H., Fox, J., & Joo, W. (2012). The remote environmental assessment laboratory’s
        acoustic library: An archive for studying soundscape ecology. Ecological Informatics, 12, 50–67.
        http://doi.org/10.1016/j.ecoinf.2012.08.001

    [13] Gasc, A., Sueur, J., Pavoine, S., Pellens, R., & Grandcolas, P. (2013). Biodiversity Sampling Using a Global
        Acoustic Approach: Contrasting Sites with Microendemics in New Caledonia. PLoS ONE, 8(5), e65311.
        http://doi.org/10.1371/journal.pone.0065311

    [14] Qi, J., Gage, S. H., Joo, W., Napoletano, B., & Biswas, S. (2007). Soundscape characteristics of an
        environment: a new ecological indicator of ecosystem health. In Wetland and Water Resource Modeling and
        Assessment: A Watershed Perspective (Vol. 20071553, pp. 201–214). http://doi.org/10.1201/9781420064155

    [15] Sueur, J., Pavoine, S., Hamerlynck, O., & Duvail, S. (2008). Rapid Acoustic Survey for Biodiversity Appraisal.
        PLoS ONE, 3(12), e4065. http://doi.org/10.1371/journal.pone.0004065

    [16] Merchant, N. D., Fristrup, K. M., Johnson, M. P., Tyack, P. L., Witt, M. J., Blondel, P., & Parks, S. E.
        (2015). Measuring acoustic habitats. Methods in Ecology and Evolution, 6(3), 257–265.
        http://doi.org/10.1111/2041-210X.12330

    [17] Mitrović, D., Zeppelzauer, M., & Breiteneder, C. (2010). Features for Content-Based Audio Retrieval.
         Advances in Computers, 78(10), 71–150. http://doi.org/10.1016/S0065-2458(10)78003-7
"""
