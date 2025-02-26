# Funciones relacionadas con el filtrado

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

import matplotlib.pyplot as plt

import os

#import soundfile


# PINK_NOISE = os.path.join("data", "pink_noise_mono_48khz_16bits.wav")
PINK_NOISE = "pink_noise.wav"
WHITE_NOISE = os.path.join("data", "white_noise_mono_48khz_16bits.wav")
NOMINAL_THIRDOCTAVE_FREC = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400,
                             500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000,
                               6300, 8000, 10000, 12500, 16000, 20000]
NOMINAL_OCTAVE_FREC = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
G =  10 ** (3/10)   # Octave frecuency ratio
FR = 1000   # Reference frequency


def cargarAudio(audio):
    # read(file) -> (rate: int, data: numpy.array)
    fs, data = wavfile.read(audio)

    return fs, data


def calcMidFrecuencies(b, x): 
    # (b, x) -> fm

    fm = FR * (G ** (x/b))  # Exact mid-band frecuencies [array]

    return fm


def calcButterFilter(fs, signal_data, fl_selected_bands, fh_selected_bands):

    N = 6   # Order of the filter
    band_levels = []   # Array con las bandas filtradas
    reference_value = 1 # Valor de referencia para obtener los niveles en dB
    
    # Aplicación de los filtros a la señal de audio
    for f_low, f_High in zip(fl_selected_bands, fh_selected_bands):
        sos = butter(N, [f_low, f_High], 'bandpass', False, 'sos', fs)  # Second Order Sections

        filtered_signal = sosfilt(sos, signal_data) # Se filtra la señal de audio cono el filtro creado

        rms = np.sqrt(np.mean(filtered_signal**2))  # Valor de amplitud RMS
        level = 20 * np.log10(rms/reference_value)  # Nivel de cada banda

        band_levels.append(level)

    return band_levels


def calcRMS(filtered_values):

    rms_values = []

    for filtered in filtered_values:
        rms = np.sqrt(np.mean(filtered**2))
        rms_values.append(rms)

    # rms_values = [np.sqrt(np.mean(filtered ** 2)) for filtered in filtered_values]

    return rms_values


def showLevels(audio, band_levels, fm, fl_selected_bands, fh_selected_bands):

    # Decidir qué frecuencias nominales utilizar
    if len(fm) == len(NOMINAL_THIRDOCTAVE_FREC):
        NOMINAL_FRECUENCIES = NOMINAL_THIRDOCTAVE_FREC

    elif len(fm) == len(NOMINAL_OCTAVE_FREC):
        NOMINAL_FRECUENCIES = NOMINAL_OCTAVE_FREC

    # Graficar niveles por bandas con barras uniformes
    widths = np.array(fh_selected_bands) - np.array(fl_selected_bands)    # Calcular ancho de las barras en escala logarítmica
    plt.figure(figsize=(10, 6))
    plt.bar(fl_selected_bands, band_levels, width=widths, align='edge', color='skyblue', edgecolor='black')
    plt.xscale('log')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Nivel (dB)')

    # Se decide el título de la gráfica dependiendo del archivo de audio
    if audio == WHITE_NOISE:
        plt.title('Niveles por bandas de octava - Ruido blanco')
    
    elif audio == PINK_NOISE:
        plt.title('Niveles por bandas de octava - Ruido rosa')

    # Personalizar el eje X para mostrar todas las frecuencias centrales
    plt.xticks(fm, labels=[f"{int(freq)} Hz" if freq >= 100 else f"{freq:.1f} Hz" for freq in NOMINAL_FRECUENCIES], rotation=45)

    # Agregar la cuadrícula
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # Personalizar la barra de estado para mostrar x e y en escala logarítmica
    ax = plt.gca()  # Get Current Axis
    ax.format_coord = lambda x, y: f"x = {x:.1f} Hz, y = {y:.1f} dB"    # Formato para mostrar Hz y dB

    plt.show()


def thirdOctaveFilter(audio, selected_bands=[NOMINAL_THIRDOCTAVE_FREC[0], NOMINAL_THIRDOCTAVE_FREC[-1]]):

    fs, signal_data = cargarAudio(audio)    # Frecuencia de muestreo y datos de la señal de audio
    print(len(signal_data))
    b = 3   # Para tercios de octava es igual a 3. Para octavas sería 1.

    x = np.arange(-16, 14)  # No incluye el último valor

    fm = calcMidFrecuencies(b, x)   # Exact mid-band frecuencies [array]
    fl = fm * (G ** (-1/(2 * b)))
    fh = fm * (G ** (1/(2 * b)))

    # Filtrar frecuencias dentro del rango proporcionado
    indexes_selected_bands = [i for i, f in enumerate(NOMINAL_THIRDOCTAVE_FREC) if selected_bands[0] <= f <= selected_bands[1]]
    fl_selected_bands = [fl[i] for i in indexes_selected_bands]
    fh_selected_bands = [fh[i] for i in indexes_selected_bands]

    # Aplicar filtro Butterworth
    band_levels = calcButterFilter(fs, signal_data, fl_selected_bands, fh_selected_bands)

    # Se muestran los niveles en dB en una gráfica
    showLevels(audio, band_levels, fm, fl_selected_bands, fh_selected_bands)

def octaveFilter(audio, selected_bands=[NOMINAL_OCTAVE_FREC[0], NOMINAL_OCTAVE_FREC[-1]]):

    fs, signal_data = cargarAudio(audio)    # Frecuencia de muestreo y datos de la señal de audio
    print(f'max:{max(signal_data)} ; min:{min(signal_data)}') # BORRAR
    b = 1   # Para tercios de octava es igual a 3. Para octavas sería 1.

    x = np.arange(-5, 5)  # No incluye el último valor
    
    fm = calcMidFrecuencies(b, x)   # Exact mid-band frecuencies [array]
    fl = fm * (G ** (-1/(2 * b)))
    fh = fm * (G ** (1/(2 * b)))

    # Filtrar frecuencias dentro del rango proporcionado
    indexes_selected_bands = [i for i, f in enumerate(NOMINAL_OCTAVE_FREC) if selected_bands[0] <= f <= selected_bands[1]]
    fl_selected_bands = [fl[i] for i in indexes_selected_bands]
    fh_selected_bands = [fh[i] for i in indexes_selected_bands]

    # Aplicar filtro Butterworth
    band_levels = calcButterFilter(fs, signal_data, fl_selected_bands, fh_selected_bands)

    # Se muestran los niveles en dB en una gráfica
    showLevels(audio, band_levels, fm, fl_selected_bands, fh_selected_bands)


# octaveFilter(PINK_NOISE)
# octaveFilter(WHITE_NOISE)
thirdOctaveFilter(PINK_NOISE)
# thirdOctaveFilter(WHITE_NOISE)
# thirdOctaveFilter(PINK_NOISE, [500, 16000])

