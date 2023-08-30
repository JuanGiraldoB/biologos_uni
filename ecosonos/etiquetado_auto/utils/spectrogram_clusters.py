from scipy import signal
import numpy as np
import soundfile as sf
import plotly.express as px
import pathlib
import colorsys
from django.templatetags.static import static
from django.conf import settings
import os


def generate_distinct_colors(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        saturation = 0.9
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(tuple(int(val * 255) for val in rgb))

    return colors


def get_plot_url(file_path, selected_clusters, df):
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
    filtered_rows = df[df.iloc[:, 0] == file_name]
    print(filtered_rows)

    filtered_df = filtered_rows.iloc[:, [0, 5, 6, 9, 10, 13]]

    print(filtered_df)

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
    fig = px.imshow(s, x=t, y=np.flip(f), aspect='auto',
                    color_continuous_scale='Rainbow')

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
        title='Spectrogram',
        xaxis_title='Time (s)',
        yaxis_title='Frequency (Hz)',
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
