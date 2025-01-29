# Funciones relacionadas con el filtrado

import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz

import matplotlib.pyplot as plt

from noise_generator import generate_white_noise, generate_pink_noise

# import soundfile


# CONSTANTES
NOMINAL_THIRDOCTAVE_FREC = [
    25,
    31.5,
    40,
    50,
    63,
    80,
    100,
    125,
    160,
    200,
    250,
    315,
    400,
    500,
    630,
    800,
    1000,
    1250,
    1600,
    2000,
    2500,
    3150,
    4000,
    5000,
    6300,
    8000,
    10000,
    12500,
    16000,
    20000,
]
NOMINAL_OCTAVE_FREC = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
G = 10 ** (3 / 10)  # Octave frecuency ratio
FR = 1000  # Reference frequency


# --------------------------------------------------------------------------------------------
def plot_filtered_signals(combined_signal):

    # Realizar la Transformada de Fourier (FFT) sobre la señal combinada
    N = len(combined_signal)
    T = 1.0 / 48000  # Periodo de muestreo
    yf = np.fft.rfft(
        combined_signal
    )  # Señal combinada en el dominio de la frecuencia
    xf = np.fft.rfftfreq(N, T)  # Frecuencias

    print(yf[0], yf[-1])

    # Graficar el espectro de la señal combinada en el dominio de la frecuencia
    plt.figure(figsize=(10, 6))
    plt.plot(
        xf, np.abs(yf) * 2 / N, color="blue", label="Señal Combinada (Espectro)"
    )
    plt.xscale("log")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Amplitud")
    plt.title("Espectro de la Señal Combinada")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.show()


def plot_filter_response(fs, fl_selected_bands, fh_selected_bands, N=16):
    # Grafica la respuesta en frecuencia de los filtros diseñados
    plt.figure(figsize=(10, 6))

    for f_low, f_high in zip(fl_selected_bands, fh_selected_bands):
        sos = butter(N, [f_low, f_high], "bandpass", False, "sos", fs)
        w, h = sosfreqz(
            sos, worN=2000, fs=fs
        )  # Respuesta en frecuencia del filtro

        # Reemplazar valores cero por un valor muy pequeño antes de calcular el logaritmo para evitar errores
        h = np.where(h == 0, 1e-10, h)

        plt.plot(
            w, 20 * np.log10(abs(h)), label=f"{f_low:.1f} - {f_high:.1f} Hz"
        )

    plt.xscale("log")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Atenuación (dB)")
    plt.title("Respuesta en Frecuencia de los Filtros")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.show()


def verify_filter_compliance(fs, fl_selected_bands, fh_selected_bands, N=16):
    green_tick = "\u2705"
    red_cross = "\u274c"

    # Compara la respuesta del filtro con los límites de atenuación de la norma ISO 61260-1
    for f_low, f_high in zip(fl_selected_bands, fh_selected_bands):
        sos = butter(N, [f_low, f_high], 'bandpass', False, 'sos', fs)
        w, h = sosfreqz(sos, worN=2000, fs=fs)
        attenuation_db = 20 * np.log10(abs(h))

        # Definir los valores de frecuencia normalizada según la tabla 5.10.2
        omega_values = [G**-4, G**-3, G**-2, G**-1, 1, G**1, G**2, G**3, G**4]
        limits_class1 = [70, 60, 40.5, 16.6, -0.4, 16.6, 40.5, 60, 70]

        for omega, limit in zip(omega_values, limits_class1):
            freq = omega * ((f_low * f_high) ** 0.5) # Frecuencia real basada en la normalización
            idx = np.argmin(np.abs(w - freq)) # Encuentra la frecuencia más cercana en la respuesta
            actual_att = attenuation_db[idx]

            if -actual_att >= limit:
                print(f"{green_tick} Freq: {freq:.1f} Hz - Attenuation: {-actual_att:.1f} dB (Limit: {limit} dB) ")
            elif -actual_att < limit:
                print(f"{red_cross} Freq: {freq:.1f} Hz - Attenuation: {-actual_att:.1f} dB (Limit: {limit} dB) ")
            


# ---------------------------------------------------------------------------------------------


def calcButterFilter(fs, signal_data, fl_selected_bands, fh_selected_bands):
    N = 16  # Orden del filtro
    band_levels = []  # Array con las bandas filtradas
    filtered_signals = np.zeros(
        (len(fl_selected_bands), len(signal_data))
    )  # Array con las señales filtradas

    # Aplicación de los filtros a la señal de audio
    for i, (f_low, f_High) in enumerate(
        zip(fl_selected_bands, fh_selected_bands)
    ):
        sos = butter(
            N, [f_low, f_High], "bandpass", False, "sos", fs
        )  # Second Order Sections

        filtered_signal = sosfilt(
            sos, signal_data
        )  # Se filtra la señal de audio cono el filtro creado
        filtered_signals[i, :] = filtered_signal

        rms = np.sqrt(np.mean(filtered_signal**2))  # Valor de amplitud RMS
        level = 20 * np.log10(rms)  # Nivel de cada banda

        band_levels.append(
            level
        )  # Niveles por bandas para representar y operar

    return filtered_signals, band_levels


def calcMidFrecuencies(b, x):
    # (b, x) -> fm
    fm = FR * (G ** (x / b))  # Exact mid-band frecuencies [array]

    return fm


def calcRMS(filtered_values):

    # Root Mean Square
    rms_values = []

    for filtered in filtered_values:
        rms = np.sqrt(np.mean(filtered**2))
        rms_values.append(rms)

    # rms_values = [np.sqrt(np.mean(filtered ** 2)) for filtered in filtered_values]

    return rms_values


def thirdOctaveFilter(
    signal_data,
    fs,
    selected_bands=[NOMINAL_THIRDOCTAVE_FREC[0], NOMINAL_THIRDOCTAVE_FREC[-1]],
):

    b = 3  # Para tercios de octava es igual a 3. Para octavas sería 1.
    x = np.arange(-16, 14)  # No incluye el último valor

    fm = calcMidFrecuencies(b, x)  # Exact mid-band frecuencies [array]
    fl = fm * (G ** (-1 / (2 * b)))
    fh = fm * (G ** (1 / (2 * b)))

    # Filtrar frecuencias dentro del rango proporcionado
    indexes_selected_bands = [
        i
        for i, f in enumerate(NOMINAL_THIRDOCTAVE_FREC)
        if selected_bands[0] <= f <= selected_bands[1]
    ]
    fl_selected_bands = [fl[i] for i in indexes_selected_bands]
    fh_selected_bands = [fh[i] for i in indexes_selected_bands]

    # Aplicar filtro Butterworth
    filtered_signals, band_levels = calcButterFilter(
        fs, signal_data, fl_selected_bands, fh_selected_bands
    )

    combined_signal = np.sum(filtered_signals, axis=0)

    plot_filtered_signals(filtered_signals[-1])

    plot_filter_response(fs, fl_selected_bands, fh_selected_bands)

    return (
        combined_signal,
        band_levels,
        fm,
        fl_selected_bands,
        fh_selected_bands,
    )

    # Se muestran los niveles en dB en una gráfica
    # showLevels(band_levels, fm, fl_selected_bands, fh_selected_bands)


def octaveFilter(
    signal_data,
    fs,
    selected_bands=[NOMINAL_OCTAVE_FREC[0], NOMINAL_OCTAVE_FREC[-1]],
):

    b = 1  # Para tercios de octava es igual a 3. Para octavas sería 1.
    x = np.arange(-5, 5)  # No incluye el último valor

    fm = calcMidFrecuencies(b, x)  # Exact mid-band frecuencies [array]
    fl = fm * (G ** (-1 / (2 * b)))
    fh = fm * (G ** (1 / (2 * b)))

    # Filtrar frecuencias dentro del rango proporcionado
    indexes_selected_bands = [
        i
        for i, f in enumerate(NOMINAL_OCTAVE_FREC)
        if selected_bands[0] <= f <= selected_bands[1]
    ]
    fl_selected_bands = [fl[i] for i in indexes_selected_bands]
    fh_selected_bands = [fh[i] for i in indexes_selected_bands]

    # Aplicar filtro Butterworth
    filtered_signals, band_levels = calcButterFilter(
        fs, signal_data, fl_selected_bands, fh_selected_bands
    )

    combined_signal = np.sum(filtered_signals, axis=0)

    verify_filter_compliance(fs, fl_selected_bands, fh_selected_bands)

    plot_filter_response(fs, fl_selected_bands, fh_selected_bands)

    plot_filtered_signals(filtered_signals[-1])

    return (
        combined_signal,
        band_levels,
        fm,
        fl_selected_bands,
        fh_selected_bands,
    )

    # Se muestran los niveles en dB en una gráfica
    # showLevels(band_levels, fm, fl_selected_bands, fh_selected_bands)


# octaveFilter(PINK_NOISE)
# octaveFilter(WHITE_NOISE)
# thirdOctaveFilter(PINK_NOISE)
# thirdOctaveFilter(WHITE_NOISE)
# thirdOctaveFilter(PINK_NOISE, [500, 16000])

white = generate_white_noise(5, 48000)
pink = generate_pink_noise(5, 48000)
octaveFilter(pink, 48000)
