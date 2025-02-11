# Autor: Samuel Bellón Elipe

# Funciones relacionadas con el filtrado

import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz

import matplotlib.pyplot as plt

from noise_generator import generate_white_noise, generate_pink_noise

# Importar constantes
from config import (
    NOMINAL_THIRDOCTAVE_FREC,
    NOMINAL_OCTAVE_FREC,
    G,
    FR,
    FILTER_ORDER,
    EPSILON,
    ACCEPTANCE_LIMITS_CLASS1,
    ACCEPTANCE_LIMITS_CLASS2
)



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

    # print(yf[0], yf[-1])

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


def plot_filter_response(fs, fl_selected_bands, fh_selected_bands):
    # Grafica la respuesta en frecuencia de los filtros diseñados
    plt.figure(figsize=(10, 6))

    for f_low, f_high in zip(fl_selected_bands, fh_selected_bands):
        sos = butter(
            FILTER_ORDER, [f_low, f_high], "bandpass", False, "sos", fs
        )
        w, h = sosfreqz(
            sos, worN=10000, fs=fs
        )  # Respuesta en frecuencia del filtro

        # Reemplazar valores cero por un valor muy pequeño antes de calcular el logaritmo para evitar errores
        h = np.where(h == 0, EPSILON, h)

        plt.plot(
            w, -20 * np.log10(abs(h)), label=f"{f_low:.1f} - {f_high:.1f} Hz"
        )

    plt.xscale("log")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Atenuación (dB)")
    plt.title("Respuesta en Frecuencia de los Filtros")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()

    # Invertir el eje Y para mostrar los valores positivos abajo y los negativos arriba
    plt.gca().invert_yaxis()

    plt.show()


def verify_filter_compliance(fs, fl_selected_bands, fh_selected_bands, band_type = "1/1"):
    filter_compliance_check = True
    green_tick = "\u2705"  # Unicode para el símbolo de check verde
    red_cross = "\u274c"  # Unicode para el símbolo de cruz roja

    print(f'EL ORDEN DE LOS FILTROS ES -> {FILTER_ORDER}')

    # Compara la respuesta del filtro con los límites de atenuación de la norma ISO 61260-1
    for i, (f_low, f_high) in enumerate(
        zip(fl_selected_bands, fh_selected_bands)
    ):
        sos = butter(
            FILTER_ORDER, [f_low, f_high], "bandpass", False, "sos", fs
        )
        w, h = sosfreqz(sos, worN=50000, fs=fs)
        # Reemplazar valores cero por un valor muy pequeño antes de calcular el logaritmo para evitar errores
        h = np.where(h == 0, EPSILON, h)
        attenuation_db = 20 * np.log10(abs(h))

        if band_type == "1/1":
            acceptance_limits = ACCEPTANCE_LIMITS_CLASS1
        elif band_type == "1/3":
            acceptance_limits = create_acceptance_limits_dicc(b=3, class_type=1)
        
        print(f"\n\n>>>>> FILTRO {i+1} <<<<<")
        # Compara la atenuación de la señal filtrada (según respuesta del filtro) con los límites de aceptación de la norma ISO 61260-1
        for omega, (low_limit, high_limit) in zip(list(acceptance_limits.keys()), list(acceptance_limits.values())): 
            freq = omega * (
                (f_low * f_high) ** 0.5
            )  # Frecuencia real basada en la normalización
            idx = np.argmin(
                np.abs(w - freq)
            )  # Encuentra la frecuencia más cercana en la respuesta del filtro
            actual_att = attenuation_db[idx]


            if low_limit <= -actual_att < high_limit:
                print(
                    f"{green_tick} Freq: {freq:.1f} Hz - Attenuation: {-actual_att:.1f} dB (Limit: {low_limit};{high_limit} dB)"
                )
                pass
            elif -actual_att < low_limit or -actual_att > high_limit:
                print(
                    f"{red_cross} Freq: {freq:.1f} Hz - Attenuation: {-actual_att:.1f} dB (Limit: {low_limit};{high_limit}dB)"
                )
                filter_compliance_check = False
    
    if filter_compliance_check:
        print(f"\n\n{green_tick} Todos los filtros cumplen con la norma ISO 61260-1")

    else:
        print(f"\n\n{red_cross} Al menos un filtro no cumple con la norma ISO 61260-1")


def create_acceptance_limits_dicc(b, class_type=1):
    
    # Crea un diccionario con los límites de aceptación de la norma ISO 61260-1 para el tipo de banda de octava seleccionado
    if b != 1:
        if class_type == 1:
            acceptance_limits = ACCEPTANCE_LIMITS_CLASS1
        else:
            acceptance_limits = ACCEPTANCE_LIMITS_CLASS2
        new_dicc = {}

        keys = list(ACCEPTANCE_LIMITS_CLASS1.keys())
        items = list(ACCEPTANCE_LIMITS_CLASS1.items())
        temp_list = [] # Lista temporal para almacenar los valores de las bandas de alta frecuencia

        # Itera sobre los 10 últimos elementos del diccionario, emepzando por el último
        for key, value in reversed(items[-10:]): 

            # Norma ISO 61260-1 apartado 5.10.3 y 5.10.4 -> High-frequency and low-frequency fractional-octave-band normalized frequency
            acceptance_limit = 1 + (((G**(1/(2*b))-1)/(G**(1/2)-1)) * (key-1))
            new_key_high = acceptance_limit
            new_key_low = 1/acceptance_limit
            
            if keys.index(key) == 9: # límites iguales para alta y baja frecuencia
                new_dicc[acceptance_limit] = value
            else:
                new_dicc[new_key_low] = value
                temp_list.append((new_key_high, value))

        # Recorro inversamente la lista temporal para añadir los valores de alta frecuencia
        for key, value in reversed(temp_list):
            new_dicc[key] = value

    return new_dicc # Devuelve el diccionario con los valores límites para el tipo de banda de octava seleccionado

# ---------------------------------------------------------------------------------------------


def calcButterFilter(fs, signal_data, fl_selected_bands, fh_selected_bands):
    band_levels = []  # Array con las bandas filtradas
    filtered_signals = np.zeros(
        (len(fl_selected_bands), len(signal_data))
    )  # Array con las señales filtradas

    # Aplicación de los filtros a la señal de audio
    for i, (f_low, f_High) in enumerate(
        zip(fl_selected_bands, fh_selected_bands)
    ):
        sos = butter(
            FILTER_ORDER, [f_low, f_High], "bandpass", False, "sos", fs
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

    return (
        combined_signal,
        band_levels,
        fm,
        fl_selected_bands,
        fh_selected_bands,
    )


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

    return (
        combined_signal,
        band_levels,
        fm,
        fl_selected_bands,
        fh_selected_bands,
    )


# octaveFilter(PINK_NOISE)
# octaveFilter(WHITE_NOISE)
# thirdOctaveFilter(PINK_NOISE)
# thirdOctaveFilter(WHITE_NOISE)
# thirdOctaveFilter(PINK_NOISE, [500, 16000])

# white = generate_white_noise(5, 48000)
# pink = generate_pink_noise(5, 48000)
# combined_signal, band_levels, fm, fl_selected_bands, fh_selected_bands = (
#     octaveFilter(pink, 48000)
# )

# verify_filter_compliance(48000, fl_selected_bands, fh_selected_bands)
# plot_filter_response(48000, fl_selected_bands, fh_selected_bands)
