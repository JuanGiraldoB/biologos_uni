import pandas as pd
import os
from maad import sound, features
# from maad.util import (date_parser, plot_correlation_map,
#                        plot_features_map, plot_features, false_Color_Spectro)

import asyncio
from .parser import my_parser
import pathlib

ALL_INDICES = ['ZCR', 'MEANt', 'VARt', 'SKEWt', 'KURTt',
               'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'ACTtFraction', 'ACTtCount',
               'ACTtMean', 'EVNtFraction', 'EVNtMean', 'EVNtCount', 'MEANf', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf',
               'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'ACI',
               'NDSI', 'rBA', 'AnthroEnergy', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC',
               'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount',
               'TFSD', 'H_Havrda', 'H_Renyi', 'H_pairedShannon', 'H_gamma', 'H_GiniSimpson', 'RAOQ',
               'AGI', 'ROItotal', 'ROIcover']


async def run_calcular_indices(raiz, archivos, progreso):
    await asyncio.to_thread(calcular_indices, raiz, archivos, progreso)


def calcular_indices(raiz, archivos, progreso):
    # path = pathlib.Path("C:/Users/JuanG/work/juancho/audios/g03/")
    df = my_parser(archivos)

    df_indices = pd.DataFrame()

    for index, row in df.iterrows():

        # get the full filename of the corresponding row
        fullfilename = row['file']
        # Save file basename
        path, filename = os.path.split(fullfilename)
        print('\n**************************************************************')
        print(filename)

        # Load the original sound (16bits) and get the sampling frequency fs
        try:
            wave, fs = sound.load(filename=fullfilename,
                                  channel='left', detrend=True, verbose=False)

        except:
            # Delete the row if the file does not exist or raise a value error (i.e. no EOF)
            df.drop(index, inplace=True)
            continue

        """ =======================================================================
                        Computation in the time domain
        ========================================================================"""

        # Parameters of the audio recorder. This is not a mandatory but it allows
        # to compute the sound pressure level of the audio file (dB SPL) as a
        # sonometer would do.
        # Sensbility microphone-35dBV (SM4) / -18dBV (Audiomoth)
        S = -35
        G = 26+16       # Amplification gain (26dB (SM4 preamplifier))

        # compute all the audio indices and store them into a DataFrame
        # dB_threshold and rejectDuration are used to select audio events.
        df_audio_ind = features.all_temporal_alpha_indices(wave, fs,
                                                           gain=G, sensibility=S,
                                                           dB_threshold=3, rejectDuration=0.01,
                                                           verbose=False, display=False)

        """ =======================================================================
                        Computation in the frequency domain
        ========================================================================"""

        # Compute the Power Spectrogram Density (PSD) : Sxx_power
        Sxx_power, tn, fn, ext = sound.spectrogram(wave, fs,
                                                   nperseg=1024, noverlap=1024//2,
                                                   verbose=False, display=False,
                                                   savefig=None)

        # compute all the spectral indices and store them into a DataFrame
        # flim_low, flim_mid, flim_hi corresponds to the frequency limits in Hz
        # that are required to compute somes indices (i.e. NDSI)
        # if R_compatible is set to 'soundecology', then the output are similar to
        # soundecology R package.
        # mask_param1 and mask_param2 are two parameters to find the regions of
        # interest (ROIs). These parameters need to be adapted to the dataset in
        # order to select ROIs
        df_spec_ind, _ = features.all_spectral_alpha_indices(Sxx_power,
                                                             tn, fn,
                                                             flim_low=[
                                                                 0, 1500],
                                                             flim_mid=[
                                                                 1500, 8000],
                                                             flim_hi=[
                                                                 8000, 20000],
                                                             gain=G, sensitivity=S,
                                                             verbose=False,
                                                             R_compatible='soundecology',
                                                             mask_param1=6,
                                                             mask_param2=0.5,
                                                             display=False)

        """ =======================================================================
                        Create a dataframe
        ========================================================================"""
        # First, we create a dataframe from row that contains the date and the
        # full filename. This is done by creating a DataFrame from row (ie. TimeSeries)
        # then transposing the DataFrame.
        df_row = pd.DataFrame(row)
        df_row = df_row.T
        df_row.index.name = 'Date'
        df_row = df_row.reset_index()

        # add scalar indices into the df_indices dataframe
        df_indices = df_indices.append(pd.concat([df_row,
                                                  df_audio_ind,
                                                  df_spec_ind], axis=1))

        progreso.archivos_completados += 1
        progreso.save()

    # Set back Date as index
    df_indices = df_indices.set_index('Date')

    df_indices.to_csv(raiz + '/indices_acusticos.csv', sep=',')
