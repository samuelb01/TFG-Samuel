import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import matplotlib.pyplot as plt

from filters3 import (
    thirdOctaveFilter,
    octaveFilter,
)  # Importar las funciones necesarias
from noise_generator import (
    generate_white_noise,
    generate_pink_noise,
)  # Importar funciones para crear ruidos

# Parámetros para generar ruidos
DURATION = 60  # Duración del audio a crear
SAMPLE_RATE = 48000  # Frecuencia de muestreo
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


class App:
    def __init__(self):
        # Configuración principal de la ventana
        self.root = tk.Tk()  # Ventana principal de la interfaz
        self.root.title("Ecualizador Gráfico")  # Título de la ventana
        self.root.geometry("900x500")  # Tamaño de la ventana

        # Variable para el tipo de ruido elegido
        self.noise_type = tk.StringVar()
        self.filter_type = tk.StringVar()
        self.combo_low_freq = ttk.Combobox()
        self.combo_high_freq = ttk.Combobox()

        # Marco para agrupar los widgets
        self.frm_options = ttk.Frame(self.root, padding=10)
        self.frm_options.grid(padx=10, pady=10)

    # Activar botón de filtrado
    def check_conditions(self, event=None):
        if all(
            [
                self.noise_type.get() != "",
                self.filter_type.get() != "",
                self.combo_low_freq.get() != "",
                self.combo_high_freq.get() != "",
            ]
        ):
            self.btn_01.state(["!disabled"])

    def change_bands(self):
        """
        Modifica dinámicamente las bandas seleccionables según el tipo de filtro elegido.

        Returns:
            list: Señal de ruido rosa.
        """
        selected_filter = self.filter_type.get()

        if selected_filter == "1/3":
            bands = NOMINAL_THIRDOCTAVE_FREC

        elif selected_filter == "1/1":
            bands = NOMINAL_OCTAVE_FREC

        return bands

    def update_bands(self):
        bands = self.change_bands()

        # Frecuencias de corte seleccionadas (en caso de estarlo)
        fl = self.combo_low_freq.get()
        fh = self.combo_high_freq.get()

        if fl == "" and fh == "":  # Ninguna seleccionada
            self.combo_low_freq["values"] = bands
            self.combo_high_freq["values"] = bands

        elif fl != "" and fh != "":  # Una de las dos
            self.combo_high_freq["values"] = bands[bands.index(float(fl)) :]
            self.combo_low_freq["values"] = bands[: bands.index(float(fh)) + 1]

        # Ambas seleccionadas
        if fl != "":
            self.combo_high_freq["values"] = bands[bands.index(float(fl)) :]
        elif fh != "":
            self.combo_low_freq["values"] = bands[: bands.index(float(fh)) + 1]

    # Realiza el filtrado
    def apply_filter(self):

        # Obtener valores de la variable actual del ruido y del tipo de filtro
        selected_noise = self.noise_type.get()
        selected_filter = self.filter_type.get()
        bandas_a_filtrar = [
            int(self.combo_low_freq.get()),
            int(self.combo_high_freq.get()),
        ]

        # Decidir tipo de filtro y de ruido para filtrar
        if (
            selected_noise != ""
            and selected_filter != ""
            and bandas_a_filtrar != ""
        ):

            if selected_noise == "WHITE NOISE":  # RUIDO BLANCO
                noise_data = generate_white_noise(DURATION, SAMPLE_RATE)

            elif selected_noise == "PINK NOISE":  # RUIDO ROSA
                noise_data = generate_pink_noise(DURATION, SAMPLE_RATE)

            if selected_filter == "1/1":  # 1/1 OCTAVA
                octaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

            elif selected_filter == "1/3":  # 1/3 OCTAVA
                thirdOctaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

        # Muestra ventana de error si no hay ruido y/o filtro seleccionado
        else:
            messagebox.showerror(
                "Advertencia",
                "Debe seleccionar un tipo de filtro, de ruido y bandas a filtrar",
            )

    def create_widgets(self):

        # Selección de ruido
        ttk.Label(self.frm_options, text="Seleccione el tipo de ruido").grid()
        radio_btn_pink = ttk.Radiobutton(
            self.frm_options,
            text="Ruido rosa",
            variable=self.noise_type,
            value="PINK NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido rosa
        radio_btn_pink.grid()

        radio_btn_white = ttk.Radiobutton(
            self.frm_options,
            text="Ruido blanco",
            variable=self.noise_type,
            value="WHITE NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido blanco
        radio_btn_white.grid()

        # Selección de tipo de filtro
        ttk.Label(self.frm_options, text="Seleccione el tipo de filtro").grid()

        radio_btn_octave = ttk.Radiobutton(
            self.frm_options,
            text="Octavas",
            variable=self.filter_type,
            value="1/1",
            command=lambda: [
                self.change_bands(),
                self.combo_low_freq.state(["!disabled"]),
                self.combo_high_freq.state(["!disabled"]),
                self.check_conditions(),
            ],
        )  # Crear botón para octavas
        radio_btn_octave.grid()

        radio_btn_third_octave = ttk.Radiobutton(
            self.frm_options,
            text="Tercios de octavas",
            variable=self.filter_type,
            value="1/3",
            command=lambda: [
                self.change_bands(),
                self.combo_low_freq.state(["!disabled"]),
                self.combo_high_freq(["!disabled"]),
                self.check_conditions(),
            ],
        )  # Crear botón para tercios de octavas
        radio_btn_third_octave.grid()

        # Selección de las bandas
        ttk.Label(
            self.frm_options, text="Seleccione las bandas a filtrar"
        ).grid()
        self.combo_low_freq = ttk.Combobox(
            state="readonly", postcommand=self.update_bands
        )
        self.combo_low_freq.grid()
        self.combo_low_freq.state(["disabled"])
        self.combo_low_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        self.combo_high_freq = ttk.Combobox(
            state="readonly", postcommand=self.update_bands
        )
        self.combo_high_freq.grid()
        self.combo_high_freq.state(["disabled"])
        self.combo_high_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        # Realizar el filtro
        btn_01 = ttk.Button(
            self.frm_options,
            text="APLICAR EL FILTRO",
            command=lambda: self.apply_filter(),
            state="disabled",
        )
        btn_01.grid()

        # Botón de reproducción
        btn_02 = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: self.play_noise(),
            state="disabled",
        )
        btn_02.grid()


app = App()
app.create_widgets()
app.root.mainloop()
