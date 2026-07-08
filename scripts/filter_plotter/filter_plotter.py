# AUTOR: SAMUEL BELLÓN ELIPE

import numpy as np
import matplotlib.pyplot as plt

from filter.filter import Filter


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
        self.ax.set_title("Niveles por bandas")

        # Graficar niveles por bandas con barras uniformes de ancho en escala logarítmica
        widths = np.array(self.fh_selected_bands) - np.array(
            self.fl_selected_bands
        )  # Calcular ancho de las barras en escala logarítmica
        
        min_level = -80  # límite inferior del eje Y (en dBFS)
        max_level = 0    # 0 dBFS

        levels = np.array(self.filtered_bands_levels)
        levels_clipped = np.maximum(levels, min_level)

        self.bars = self.ax.bar(
            self.fl_selected_bands,
            levels_clipped - min_level,
            bottom=min_level,
            width=widths,
            align="edge",
            color="skyblue",
            edgecolor="black",
        )

        self.ax.set_ylim(min_level, max_level)
        self.ax.axhline(0, color="red", linestyle="--", linewidth=1)
        
        # Configurar el eje X en escala logarítmica y etiquetar los ejes
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frecuencia (Hz)", fontsize=10)
        self.ax.set_ylabel("Nivel (dBFS)", fontsize=10)

        # Personalizar el eje X para mostrar todas las frecuencias centrales
        self.ax.set_xticks(self.nominal_frequencies)
        self.ax.set_xticklabels(
            [
                f"{int(freq)} Hz" if freq >= 100 else f"{freq:.1f} Hz"
                for freq in self.nominal_frequencies
            ],
            rotation=45,
            fontsize=7
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