# import acoustics.generator
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

from acoustics.signal import OctaveBand
from acoustics.signal import bandpass
import acoustics
# from acoustics.standards.iec_61260_1_2014 import nominal_center_frequency

import os

PINK_NOISE = os.path.join("data", "pink_noise_mono_48khz_16bits.wav")
WHITE_NOISE = os.path.join("data", "white_noise_mono_48khz_16bits.wav")
NOMINAL_THIRDOCTAVE_FREC = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400,
                            500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000,
                            6300, 8000, 10000, 12500, 16000, 20000]
NOMINAL_OCTAVE_FREC = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]



def load_file(signal):
    """_summary_

    Args:
        signal (str): señal a leer

    Returns:
        fs (int): Frecuencia de muestreo
        data (numpy.ndarray): valores de amplitud de la señal
    """
    fs, data = wavfile.read(signal)

    return fs, data


def calc_bands(fstart, fstop, fraction):
    """calcula las frecuencias límites y centrales de cada banda

    Args:
        fstart (int): frecuencia de inicio
        fstop (int): frecuencia de parada
        fraction (int):  Fracción de octava para las bandas (1 para octavas y 3 para tercios de octava)

    Returns:
        bands.lower (numpy.ndarray): frecuencias inferiores de las bandas
        bands.upper (numpy.ndarray): frecuencias superiores de las bandas
        bands.center (numpy.ndarray): frecuencias centrales de las bandas
    """    
    bands = OctaveBand(fstart=fstart, fstop=fstop, fraction=fraction)

    return bands.lower, bands.upper, bands.center


def bands_filter(fs, signal_data, lower_frecencies, upper_frequencies):
    """Realiza el filtrado a cada banda

    Args:
        fs (int): frecuencia de muestreo
        signal_data (numpy.ndarray): valores de amplitud de la señal
        lower_frecencies (list): frecuencias inferiores de las bandas
        upper_frequencies (list): frecuencias superiores de las bandas

    Returns:
        band_levels (list): niveles de cada banda
    """ 
    band_levels = []

    for f_low, f_high in zip(lower_frecencies, upper_frequencies):
        # Filtrado y cálculo de nivel de cada banda de la señal
        filtered_signal = bandpass(signal_data, f_low, f_high, fs)
        rms = np.sqrt(np.mean(filtered_signal ** 2))  # RMS de la señal filtrada
        band_levels.append(20 * np.log10(rms))  # Nivel en dB
    
    return band_levels
    


def show_levels(band_levels, nominal_central_frequencies, lower_frequencies, upper_frequencies):
    """Muestra una gráfica de niveles por banda

    Args:
        signal (str): señal de referencia
        band_levels (list): niveles de caada banda
        nominal_central_frequencies (_type_): frecuencias centrales nominales según norma ISO 61260-1:2014
        lower_frequencies (_type_): frecuencias inferiores de las bandas
        upper_frequencies (_type_): frecuencias superiores de las bandas
    """
    widths = np.array(upper_frequencies) - np.array(lower_frequencies)  # Anchura de las bandas
    plt.figure(figsize=(10, 6))
    plt.bar(lower_frequencies, band_levels, width=widths, align='edge', color='skyblue', edgecolor='black')
    plt.xscale('log')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Nivel (dB)')
    # plt.title(f'Niveles por bandas de {"tercios de octava" if len(nominal_central_frequencies) > len(NOMINAL_OCTAVE_FREC) else "octava"} - {os.path.basename(signal)}')
    plt.xticks(nominal_central_frequencies, labels=[f"{int(f)} Hz" for f in nominal_central_frequencies], rotation=45)
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def third_octave_filter(signal, range=[NOMINAL_THIRDOCTAVE_FREC[0], NOMINAL_THIRDOCTAVE_FREC[-1]]):
    """Realiza el filtrado en tercios de octava y lo muestra

    Args:
        signal (str): signal a filtrar
        range (list, optional): Array con dos valores, la banda inicial y final. Defaults to [NOMINAL_THIRDOCTAVE_FREC[0], NOMINAL_THIRDOCTAVE_FREC[-1]].
    """
    fs, signal_data = load_file(signal)
    lower_frequencies, upper_frequencies, central_frequencies = calc_bands(range[0], range[1], 3)
    band_levels = bands_filter(fs, signal_data, lower_frequencies, upper_frequencies)
    show_levels(signal, band_levels, NOMINAL_THIRDOCTAVE_FREC, lower_frequencies, upper_frequencies)


def octave_filter(signal_data, fs, range=[NOMINAL_OCTAVE_FREC[0], NOMINAL_OCTAVE_FREC[-1]]):
    """Realiza el filtrado octavas y lo muestra

    Args:
        signal (str): signal a filtrar
        range (list, optional): Array con dos valores, la banda inicial y final. Defaults to [NOMINAL_THIRDOCTAVE_FREC[0], NOMINAL_THIRDOCTAVE_FREC[-1]].
    """
    # signal_data = load_file(signal)
    lower_frequencies, upper_frequencies, central_frequencies = calc_bands(range[0], range[1], 1)
    band_levels = bands_filter(fs, signal_data, lower_frequencies, upper_frequencies)
    show_levels(band_levels, NOMINAL_OCTAVE_FREC, lower_frequencies, upper_frequencies)

def white_noise_generator(duration, fs):
    sample_number = int(duration*fs)
    white_noise = np.random.randn(sample_number)

    return white_noise

fs = 48000

white_noise = white_noise_generator(60, fs)

# octave_filter(white_noise, fs)

# # Ejecución
# third_octave_filter(PINK_NOISE)
# octave_filter(PINK_NOISE)
# third_octave_filter(WHITE_NOISE)
# octave_filter(WHITE_NOISE)

# third_octave_filter(PINK_NOISE, [500, 8000])

import numpy as np
from scipy.io.wavfile import write

def white_noise_generator(duration, fs):
    sample_number = int(duration * fs)
    white_noise = np.random.randn(sample_number)
    
    # Normaliza el ruido blanco a un rango adecuado para audio (por ejemplo, entre -1 y 1)
    white_noise = white_noise / np.max(np.abs(white_noise))  # Normaliza a -1 a 1

    return 12589 * white_noise

fs = 48000  # Frecuencia de muestreo de 48 kHz
duration = 60  # Duración de 60 segundos

# Generar el ruido blanco
white_noise = white_noise_generator(duration, fs)

# Guardar el ruido blanco como un archivo WAV
write('ruido_blanco.wav', fs, (white_noise * 32767).astype(np.int16))  # Normaliza a 16 bits PCM
