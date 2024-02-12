import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import soundfile as sf
import plotly.express as px
import pathlib
import colorsys
from django.templatetags.static import static
from django.conf import settings
import os
import cv2
import matplotlib
# Use the Agg backend to avoid threading problems
matplotlib.use('Agg')


def generate_distinct_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        saturation = 0.9
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(tuple(int(val * 255) for val in rgb))

    return colors


def generate_spectrogram_with_clusters_plot(file_path, selected_clusters, df):
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

    # File name to match
    file_name = pathlib.Path(file_path).name

    # Filter rows where the file name is in column index 0
    filtered_rows = df[df.iloc[:, 0] == file_path]
    filtered_df = filtered_rows.iloc[:, [0, 5, 6, 9, 10, 13]]

    try:
        x, fs = sf.read(file_path)
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
    wn = "hamming"
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

    fig = px.imshow(s, x=t, y=f, aspect='auto',
                    color_continuous_scale='Rainbow', origin='lower')

    config = {
        'toImageButtonOptions': {
            'format': 'svg',  # one of png, svg, jpeg, webp
            'filename': 'custom_image',
            'height': 500,
            'width': 700,
            'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }

    fig.update_layout(
        title='Espectrograma',
        xaxis_title='Tiempo (s)',
        yaxis_title='Frecuencia (Hz)',
    )

    # Add rectangles to the plot
    ec = generate_distinct_colors(50)
    for i in range(filtered_df.shape[0]):
        clus = int(filtered_df.iloc[i, -1])

        if clus in selected_clusters:
            start = filtered_df.iloc[i, 1]
            end = filtered_df.iloc[i, 2]
            fv_min = filtered_df.iloc[i, 3]
            fv_max = filtered_df.iloc[i, 4]

            fig.add_shape(
                type="rect",
                x0=start,
                x1=end,
                y0=fv_min,
                y1=fv_max,
                line=dict(color=f"rgb{ec[clus]}", width=2),
            )

    fig.add_annotation(
        text=file_name,
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        showarrow=False,
    )

    relative_path = os.path.join(
        'etiquetado_auto', 'plot', 'clusters_plot.html')

    static_folder = os.path.join(
        settings.BASE_DIR, 'etiquetado_auto', 'static')
    fig_path = os.path.join(static_folder, relative_path)

    fig.write_html(fig_path, config=config)

    fig_url = static(relative_path)

    return fig_url


def generate_spectrogram_representative_element_plot(metodologia_output, df, representativo_index):
    table = df
    representativo = metodologia_output.representativo
    # selección de un cluster numero minimo y maximo dado por la tabla puede cambiar este numero según los clusters que haya
    representativo_row = representativo[representativo_index]

    # audio = table[representativo[sel]][0]
    audio = table.iloc[representativo_row, 0]

    # audio_sel = ruta+"/"+audio
    x, fs = sf.read(audio)

    if len(x.shape) == 1:
        senal_audio = x
    else:
        x = x.mean(axis=1)
        x = np.squeeze(x)
        senal_audio = x

    wn = "hamming"
    size_wn = 1024
    noverlap = size_wn / 2
    nfft = size_wn * 2
    nmin = round(len(senal_audio) / (60 * fs))
    nperseg = nmin * size_wn

    frecuency, time, intensity = signal.spectrogram(senal_audio, fs=fs, window=wn, nfft=nfft, nperseg=1024,
                                                    noverlap=512)

    frecuency = np.flip(frecuency)

    img = np.int_((cv2.flip(20*(np.log10(np.abs(intensity))), 0)))

    fig = px.imshow(img, x=time, y=frecuency, aspect='auto',
                    color_continuous_scale='Rainbow', origin='lower')

    fig.update_layout(
        title='Espectrograma',
        xaxis_title='Tiempo (s)',
        yaxis_title='Frecuencia (Hz)',
    )

    start = table.iloc[representativo_row, 5]
    end = table.iloc[representativo_row, 6]
    fv_min = table.iloc[representativo_row, 9]  # frecuencia vocal minima
    fv_max = table.iloc[representativo_row, 10]  # frecuencia vocal maxima

    # Add a rectangle to highlight the region
    fig.add_shape(
        type="rect",
        x0=start,
        x1=end,
        y0=fv_min - 150,
        y1=fv_max + 150,
        line=dict(color="white", width=2),
    )

    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Frequency")
    fig.update_layout(title_text="Spectrogram with Highlighted Region")

    relative_path = os.path.join(
        'etiquetado_auto', 'plot', 'representative_plot.html')

    static_folder = os.path.join(
        settings.BASE_DIR, 'etiquetado_auto', 'static')
    fig_path = os.path.join(static_folder, relative_path)

    fig.write_html(fig_path)

    fig_url = static(relative_path)

    return fig_url


async def run_generate_hourly_pattern_graph_of_the_sonotype(dft, progreso):
    await asyncio.to_thread(generate_hourly_pattern_graph_of_the_sonotype, dft, progreso)


def generate_hourly_pattern_graph_of_the_sonotype(dft, progreso):

    dft = pd.DataFrame(dft, columns=[
        'File', 'Month', 'Day', 'Hour', 'Length', 'Fdom', 'FminVoc', 'FmaxVoc', 'Cluster'])

    files2 = []

    for cnt in range(len(dft['File'])):
        file = dft['File'][cnt].split(os.sep)[-1]

        s = extract_prefix_from_filename(file)

        files2.append(s)

    dft['File'] = files2
    sitios = list(dft['File'].unique())
    sonotipos = list(dft['Cluster'].unique())
    sitios.sort()
    sonotipos.sort()
    Dmin = int(dft.Day.min())
    Dmax = int(dft.Day.max())
    x = list(range(24))

    fig_urls = []

    # Crear las graficas
    for i, son in enumerate(sonotipos):
        fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))

        # Conteo por sonotipo, por sitio
        subSet = dft[dft['Cluster'] == son]

        # Conteo por hora
        L = []
        for j in range(0, 24):
            cont = []
            for k in range(Dmin, Dmax+1):
                b = subSet[subSet.Hour.isin([j, j]) & subSet.Day.isin([k, k])]
                cont.append(len(list(b.Day)))
            L.append(np.sum(cont))
        L = np.array(L)

        # Crear gráfica radial con línea
        theta = np.linspace(0, 2*np.pi, len(x), endpoint=False)
        radii = L
        ax.plot(theta, radii)

        # Personalizar gráfica
        ax.set_title(f"Sonotipo {int(son)}", fontsize=9)
        ax.set_xticks(theta)
        ax.set_xticklabels(x)
        ax.yaxis.grid(True)
        ax.set_rlabel_position(0)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        plt.tight_layout()

        # Generate a URL for each saved figure

        relative_path = os.path.join(
            'etiquetado_auto', 'img', f"polar_plot_{i}.png")

        if os.path.exists(relative_path):
            os.remove(relative_path)

        static_folder = os.path.join(
            settings.BASE_DIR, 'etiquetado_auto', 'static')
        fig_path = os.path.join(static_folder, relative_path)

        plt.savefig(fig_path, dpi=300, bbox_inches='tight')

        # Get the URL for the saved figure
        fig_url = static(relative_path)
        fig_urls.append(fig_url)

        progreso.archivos_completados += 1
        progreso.save()

    plt.close()


def extract_prefix_from_filename(filename):
    if '__' in filename:
        prefix = filename.split('__')[0]
    else:
        prefix = filename.split('_')[0]

    return prefix
