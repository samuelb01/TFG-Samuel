# Autor: Samuel Bellón Elipe

import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz

# Importar constantes
from config import (
    NOMINAL_THIRDOCTAVE_FREC,
    NOMINAL_OCTAVE_FREC,
    G,
    FR,
    FILTER_ORDER,
    SAMPLE_RATE,
    EPSILON,
    ACCEPTANCE_LIMITS_CLASS1,
    ACCEPTANCE_LIMITS_CLASS2,
)


class Filters:
    def __init__(self, data):
        self.data = data
        self.fs = SAMPLE_RATE

    def get_frequencies(self, filter_type):
        """
        Obtiene las frecuencias de corte de los filtros de octava o tercio de octava.
        Las inferiores (fl), medias (fm) y superiores (fh)
        """
        if filter_type == "octave":
            nominal_frequencies = NOMINAL_OCTAVE_FREC
            b = 1
        elif filter_type == "third-octave":
            nominal_frequencies = NOMINAL_THIRDOCTAVE_FREC
            b = 3

        x = np.arange(-5, 5)  # No incluye el último valor

        # Arrays con los valores de frecuencias
        fm = FR * (G ** (x / b))
        fl = fm * (G ** (-1 / (2 * b)))
        fh = fm * (G ** (1 / (2 * b)))

        return nominal_frequencies, fl, fm, fh

    def get_selected_frequencies(self, nominal_frequencies, fl, fm, fh):
        """
        Selecciona las frecuencias inferiores, medias y altas para las bandas elegidas.
        """
        # Filtrar frecuencias dentro del rango proporcionado
        indexes_selected_bands = [
            i
            for i, f in enumerate(nominal_frequencies)
            if self.selected_bands[0] <= f <= self.selected_bands[1]
        ]
        fl_selected_bands = [fl[i] for i in indexes_selected_bands]
        fm_selected_bands = [fm[i] for i in indexes_selected_bands]
        fh_selected_bands = [fh[i] for i in indexes_selected_bands]

        return fl_selected_bands, fm_selected_bands, fh_selected_bands
    
    @staticmethod
    def create_butter_bandpass_filters(fl, fh, fs, order=FILTER_ORDER):
        """
        Crea los filtros Butterworth paso-banda para las bandas seleccionadas.
        """
        sos = []
        for low, high in zip(fl, fh):
            sos.append(
                butter(
                    order,
                    [low, high],
                    btype="band",
                    fs=fs,
                    output="sos",
                )
            )
        return sos

    def octave_filter(
        self, selected_bands=[NOMINAL_OCTAVE_FREC[0], NOMINAL_OCTAVE_FREC[-1]]
    ):
        self.selected_bands = selected_bands
        nominal_frequencies, fl, fm, fh = self.get_frequencies("octave")

        # Obtengo frecuencias de corte delos filtros seleccionados
        fl_selected_bands, fm_selected_bands, fh_selected_bands = (
            self.get_selected_frequencies(NOMINAL_OCTAVE_FREC, fl, fm, fh)
        )

        # Creo los filtros
        sos_butter_filters = self.create_butter_bandpass_filters(
            fl_selected_bands, fh_selected_bands, self.fs
        )

        print(sos_butter_filters[0])
        # Aplico los filtros
        
        
