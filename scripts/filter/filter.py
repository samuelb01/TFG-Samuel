# Autor: Samuel Bellón Elipe

import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Importar constantes
from config import (
    NOMINAL_THIRDOCTAVE_FREQ,
    NOMINAL_OCTAVE_FREQ,
    G,
    FR,
    FILTER_ORDER,
    SAMPLE_RATE,
    EPSILON,
    ACCEPTANCE_LIMITS_CLASS1,
    ACCEPTANCE_LIMITS_CLASS2,
)


class Filter:
    def __init__(self):
        """Constructor de la clase Filter"""
        self.filter_type = None
        self.nominal_frequencies = None
        self.fs = SAMPLE_RATE
        self.fl_selected_bands = None
        self.fm_selected_bands = None
        self.fh_selected_bands = None
        self.signal = None
        self.filtered_signal = None
        self.filtered_bands = None
        self.filtered_bands_levels = None

    def get_frequencies(self):
        """
        Obtiene las frecuencias de corte de los filtros de octava o tercio de octava.
        Las inferiores (fl), medias (fm) y superiores (fh)
        """
        if self.filter_type == "octave":
            b = 1
            x = np.arange(-5, 5)  # No incluye el último valor
        elif self.filter_type == "third-octave":
            b = 3
            x = np.arange(-16, 14)  # No incluye el último valor

        # Arrays con los valores de frecuencias
        fm = FR * (G ** (x / b))
        fl = fm * (G ** (-1 / (2 * b)))
        fh = fm * (G ** (1 / (2 * b)))

        return fl, fm, fh

    def get_selected_frequencies(self, selected_bands, fl, fm, fh):
        """
        Selecciona las frecuencias inferiores, medias y altas para las bandas elegidas.
        """
        # Filtrar frecuencias dentro del rango proporcionado
        indexes_selected_bands = [
            i
            for i, f in enumerate(self.nominal_frequencies)
            if selected_bands[0] <= f <= selected_bands[1]
        ]
        self.fl_selected_bands = [fl[i] for i in indexes_selected_bands]
        self.fm_selected_bands = [fm[i] for i in indexes_selected_bands]
        self.fh_selected_bands = [fh[i] for i in indexes_selected_bands]

    def create_butter_bandpass_filters(self, order=FILTER_ORDER):
        """
        Crea los filtros Butterworth paso-banda para las bandas seleccionadas.
        """
        sos = []
        for low, high in zip(self.fl_selected_bands, self.fh_selected_bands):
            sos.append(
                butter(
                    order,
                    [low, high],
                    btype="bandpass",
                    output="sos",
                    fs=self.fs,
                )
            )

        return sos

    def apply_sos_filter(self, sos_butter_filters):
        """Aplica los filtros a la señal de entrada"""
        # Inicializar matriz de bandas filtradas
        self.filtered_bands = np.zeros(
            (len(self.fm_selected_bands), len(self.signal))
        )
        for i, sos in enumerate(sos_butter_filters):
            filtered_data = sosfilt(sos, self.signal)
            self.filtered_bands[i, :] = filtered_data
    
    def calc_signal_band_levels(self):
        """Calcula los niveles de las bandas de la señal filtrada"""
        self.filtered_bands_levels = []

        for band in self.filtered_bands:
            rms = np.sqrt(np.mean(band**2))  # Valor de amplitud RMS
            level = 20 * np.log10(rms)  # Nivel de cada banda
            self.filtered_bands_levels.append(level)

    def recombine_bands(self):
        """Recombina las bandas filtradas para obtener la señal final filtrada"""
        self.filtered_signal = np.sum(self.filtered_bands, axis=0)

    def octave_filter(
        self, selected_bands=[NOMINAL_OCTAVE_FREQ[0], NOMINAL_OCTAVE_FREQ[-1]]
    ):
        """Filtra la señal con filtro de octava"""
        self.filter_type = "octave"
        self.nominal_frequencies = NOMINAL_OCTAVE_FREQ

        # Obtengo frecuencias de corte hy centrales de los filtros seleccionados
        fl, fm, fh = self.get_frequencies()

        # Obtengo las frecuencias de corte y centrales para las bandas seleccionadas
        self.get_selected_frequencies(
            selected_bands, fl, fm, fh
        )

        # Creo los filtros
        sos_butter_filters = self.create_butter_bandpass_filters()

        # Aplico los filtros
        self.apply_sos_filter(sos_butter_filters)

        # Calculo niveles en dB
        self.calc_signal_band_levels()

        # Recombino las bandas filtradas para obtener la señal final filtrada
        self.recombine_bands()

    def third_octave_filter(
        self,
        selected_bands=[
            NOMINAL_THIRDOCTAVE_FREQ[0],
            NOMINAL_THIRDOCTAVE_FREQ[-1],
        ],
    ):
        """Filtra la señal con filtro de octava"""
        self.filter_type = "third-octave"
        self.nominal_frequencies = NOMINAL_THIRDOCTAVE_FREQ

        # Obtengo frecuencias de corte hy centrales de los filtros seleccionados
        fl, fm, fh = self.get_frequencies()

        # Obtengo las frecuencias de corte y centrales para las bandas seleccionadas
        self.get_selected_frequencies(
            selected_bands, fl, fm, fh
        )

        # Creo los filtros
        sos_butter_filters = self.create_butter_bandpass_filters()

        # Aplico los filtros
        self.apply_sos_filter(sos_butter_filters)

        # Calculo niveles en dB
        self.calc_signal_band_levels()

        # Recombino las bandas filtradas para obtener la señal final filtrada
        self.recombine_bands()

    def verify_filter_compliance(self, filter_class="1"):
        """ Verifica si la señal filtrada cumple con los límites de aceptación de la norma ISO 61260-1""" 
        filter_compliance_check = True
        green_tick = "\u2705"  # Unicode para el símbolo de check verde
        red_cross = "\u274c"  # Unicode para el símbolo de cruz roja

        if filter_class == "1":
            acceptance_limits = ACCEPTANCE_LIMITS_CLASS1
        elif filter_class == "2":
            acceptance_limits = ACCEPTANCE_LIMITS_CLASS2

        print(f'EL ORDEN DE LOS FILTROS ES -> {FILTER_ORDER}')

        all_sos = self.create_butter_bandpass_filters()

        for i, (sos, f_low, f_high) in enumerate(
            zip(all_sos, self.fl_selected_bands, self.fh_selected_bands)
        ):
            # Respuesta en frecuencia del filtro
            w, h = sosfreqz(sos, worN=50000, fs=self.fs)

            # Reemplazar valores cero por un valor muy pequeño antes de calcular el logaritmo para evitar errores
            h = np.where(h == 0, EPSILON, h)
            attenuation_db = 20 * np.log10(abs(h))

            if self.filter_type == "octave":
                acceptance_limits = acceptance_limits
            elif self.filter_type == "third-octave":
                acceptance_limits = self.create_acceptance_limits_dicc(acceptance_limits, b=3)
        
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

    @staticmethod
    def create_acceptance_limits_dicc(acceptance_limits, b):
        """ Crea un diccionario con los límites de aceptación de la norma ISO 61260-1 para el tipo de banda de octava seleccionado """
        if b != 1:
            new_dicc = {}

            keys = list(acceptance_limits.keys())
            items = list(acceptance_limits.items())
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
