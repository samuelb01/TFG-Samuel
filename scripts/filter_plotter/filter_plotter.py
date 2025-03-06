# AUTOR: SAMUEL BELLÓN ELIPE

import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from filter.filter import Filter

from config import EPSILON

class FilterPlotter(Filter):
    def __init__(self, filter_instance):
        """
        Constructor de FilterPlotter.
        Recibe una instancia de una clase de filtro y hereda todos sus atributos.
        """
        super().__init__()
        self.__dict__.update(filter_instance.__dict__)
        self.ax = None
        self.figure = None
        self.bars = None
        self.annotation = None

    def plot_filtered_signal_levels(self):
        """Muestra los niveles de las bandas fitlradas de la señal"""
        # Crear una figura de Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        # ax = figure.add_subplot(111)
        self.ax.set_title("Niveles por bandas")

        # Graficar niveles por bandas con barras uniformes de ancho en escala logarítmica
        widths = np.array(self.fh_selected_bands) - np.array(
            self.fl_selected_bands
        )  # Calcular ancho de las barras en escala logarítmica
        self.bars = self.ax.bar(
            self.fl_selected_bands,
            self.filtered_bands_levels,
            width=widths,
            align="edge",
            color="skyblue",
            edgecolor="black",
        )

        # Obtener el nivel máximo de las bandas y agregar 15 dB
        y_max = max(self.filtered_bands_levels) + 15
        # Ajustar límites del eje Y
        self.ax.set_ylim(0, y_max)

        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frecuencia (Hz)")
        self.ax.set_ylabel("Nivel (dB)")

        # Personalizar el eje X para mostrar todas las frecuencias centrales
        self.ax.set_xticks(self.nominal_frequencies)
        self.ax.set_xticklabels(
            [
                f"{int(freq)} Hz" if freq >= 100 else f"{freq:.1f} Hz"
                for freq in self.nominal_frequencies
            ],
            rotation=45,
        )

        # Agregar la cuadrícula
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        self.figure.tight_layout()
    
    def create_scatter_points(self):
        """ Crear puntos en la misma posición que las barras, cambiarán con la ecualización """
        self.scatter_points = self.ax.scatter(
            self.fm_selected_bands, self.filtered_bands_levels, color="red", zorder=3
        )

    def create_annotation_to_show_levels(self):
        """ Crear el "annotation" para mostrar el nivel en dB """
        self.annotation = self.ax.annotate(
            "",  # Texto inicial vacío
            xy=(0, 0),  # Posición inicial
            xytext=(0, 5),  # Desplazamiento del texto respecto al punto (xy)
            textcoords="offset points",  # La posición de xytext es relativa a xy
            bbox=dict(
                boxstyle="round,pad=0.3", fc="yellow", alpha=0.8
            ),  # Cuadro de fondo
            fontsize=10,  # Tamaño del texto
            color="black",  # Color del texto
            ha="center",  # Alinear horizontalmente el texto en el centro
            visible=False,  # Ocultar al inicio
        )

    def on_hover(self, event, plot_canvas):
        """Función para mostrar el valor al pasar el cursor"""
        if (
            event.inaxes == self.ax
        ):  # Verifica si el cursor está dentro del área de la gráfica
            for bar, level, freq in zip(
                self.bars,
                self.filtered_bands_levels,
                self.fm_selected_bands,
            ):
                contains, _ = bar.contains(
                    event
                )  # Verifica si el cursor está sobre una barra
                if contains:
                    # Posicionar la anotación encima de la barra
                    self.annotation.set_text(
                        f"{level:.1f} dB"
                    )  # Muestra el nivel en dB
                    self.annotation.xy = (
                        freq,
                        level + 1,
                    )  # Lo coloca sobre la barra
                    self.annotation.set_visible(True)  # Lo hace visible
                    plot_canvas.draw_idle()  # Redibuja solo si hay cambios
                    return
        self.annotation.set_visible(
            False
        )  # Oculta la anotación si no está sobre una barra
        plot_canvas.draw_idle()

    def plot_filter_response(self):
        """ Muestra la respuesta en frecuencia de los filtros"""
        plt.figure(figsize=(10, 5))

        all_sos = self.create_butter_bandpass_filters()

        for sos, f_low, f_high in zip(all_sos, self.fl_selected_bands, self.fh_selected_bands):
            # Respuesta en frecuencia del filtro
            w, h = sosfreqz(sos, worN=50000, fs=self.fs)

            print(w)

            # Reemplazar valores cero por un valor muy pequeño antes de calcular el logaritmo para evitar errores
            h = np.where(h == 0, EPSILON, h)
            attenuation_db = 20 * np.log10(abs(h))

            plt.plot(
                w, attenuation_db, label=f"{f_low:.1f} - {f_high:.1f} Hz"
            )

        plt.xscale("log")
        plt.xlabel("Frecuencia (Hz)")
        plt.ylabel("Ganancia (dB)")
        plt.title("Respuesta en Frecuencia de los Filtros")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()

        plt.show()

    def plot_frequency_spectrum(self):
        """
        Calcula y grafica el espectro de frecuencia de la señal filtrada.
        """
        # Calculamos la FFT de la señal filtrada
        fft_signal = np.fft.fft(self.filtered_bands[6])
        
        # Obtenemos las frecuencias correspondientes
        freqs = np.fft.fftfreq(len(fft_signal), d=1/self.fs)
        
        # Tomamos solo la parte positiva del espectro
        half = len(fft_signal) // 2
        fft_signal = fft_signal[:half]
        freqs = freqs[:half]
        
        # Calculamos la magnitud de la FFT
        magnitude = np.abs(fft_signal)
        
        # Graficamos el espectro de frecuencia
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, magnitude)
        plt.title("Espectro de Frecuencia de la Señal Filtrada")
        plt.xlabel("Frecuencia (Hz)")
        plt.ylabel("Magnitud")
        plt.grid(True)
        plt.show()