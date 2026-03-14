from noise_generator.noise_generator import NoiseGenerator
from filter.filter import Filter
from audio_player.audio_player import AudioPlayer
from filter_plotter.filter_plotter import FilterPlotter

import tkinter as tk
from tkinter import ttk, messagebox, TclError, filedialog

import numpy as np
import csv

import sys
import wave
from pathlib import Path
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import NOMINAL_OCTAVE_FREQ, NOMINAL_THIRDOCTAVE_FREQ, DURATION, SAMPLE_RATE


class GUI:
    def __init__(self):
        """Constructor de la clase GUI"""
        self.noise_generator = NoiseGenerator()
        self.filter = Filter()
        self.audio_player = AudioPlayer()

        self.main_graph = None
        self.equalizer_graph = None

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_app)
        self.root.title("PROYECTO SAMUEL")
        
        # Habilitar redimensionamiento
        self.root.resizable(True, True)
        self.root.update_idletasks()
        self.root.geometry("1200x600") # Tamaño inicial de la ventana
        self.root.update()

        self.main_window = ttk.Notebook(self.root)  # Ventana principal
        self.tab_main = None
        self.tab_equalizer = None

        self.noise_type = tk.StringVar()
        self.band_type = tk.StringVar()
        self.filter_type = tk.StringVar()

        # Diccionario para valores de los ttk.Entry del usuario y con los tk.Entry
        self.user_data_entry_vars = dict()
        self.user_data_entry_dict = dict()

        self.create_main_tab()
        # self.create_equalizer_tab()

        # # 85% del ancho de la pantalla para el gráfico y el 15% para el menú de opciones
        # self.tab_main.grid_columnconfigure(1, weight=85)
        # self.tab_main.grid_columnconfigure(0, weight=15)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_window.grid(row=0, column=0, sticky="nsew")

        self.root.mainloop()

    def clear_frame(self, frame):
        """Elimina todos los widgets dentro del frame"""
        for widget in frame.winfo_children():
            widget.destroy()

    @staticmethod
    def disable_widgets(frame):
        for widget in frame.winfo_children():
            try:
                widget.config(state="disabled")
            except tk.TclError:
                pass  # Algunos widgets como Frames no tienen "state", así que los ignoramos.

    @staticmethod
    def enable_widgets(frame):
        for widget in frame.winfo_children():
            try:
                widget.config(state="!disabled")
            except tk.TclError:
                pass  # Algunos widgets como Frames no tienen "state", así que los ignoramos.

    def on_validate_user_data_input(self, P):
        # Permitir estados intermedios mientras escribe
        if P in ("", "-", ".", "-."):
            return True

        # Solo un signo negativo y al inicio
        if P.count("-") > 1:
            return False
        if "-" in P and not P.startswith("-"):
            return False

        # Quitar signo para analizar
        s = P[1:] if P.startswith("-") else P

        # Solo un punto decimal
        if s.count(".") > 1:
            return False

        if "." in s:
            left, right = s.split(".", 1)

            # Parte entera: máximo 3 dígitos
            if left != "" and (not left.isdigit() or len(left) > 3):
                return False

            # Parte decimal: máximo 2 dígitos
            if right != "" and (not right.isdigit() or len(right) > 2):
                return False

        else:
            # Sin punto: máximo 3 dígitos enteros
            if not s.isdigit() or len(s) > 3:
                return False

        return True
            
    def is_valid_db_string(self, s):
        """Valida si una cadena tiene un formato de dB aceptado (máx 3 enteros, máx 2 decimales)"""
        s = s.strip()
        if not s:
            return False

        # Quitar signo para analizar
        val_s = s[1:] if s.startswith("-") else s

        if not val_s:  # Caso donde solo hay un "-"
            return False

        if "." in val_s:
            parts = val_s.split(".")
            if len(parts) != 2:
                return False
            left, right = parts

            # Parte entera: máximo 3 dígitos
            if left != "" and (not left.isdigit() or len(left) > 3):
                return False
            # Parte decimal: máximo 2 dígitos
            if right != "" and (not right.isdigit() or len(right) > 2):
                return False
        else:
            # Sin punto: máximo 3 dígitos enteros
            if not val_s.isdigit() or len(val_s) > 3:
                return False

        return True

    def create_main_tab(self):
        """Crear la pestaña principal de la interfaz"""
        self.tab_main = ttk.Frame(self.main_window)
        self.main_window.add(self.tab_main, text="Main")

        # Configurar pesos de las columnas: la gráfica (col 1) tendrá más peso que el menú (col 0)
        self.tab_main.grid_columnconfigure(0, weight=1)
        self.tab_main.grid_columnconfigure(1, weight=4)
        self.tab_main.grid_rowconfigure(0, weight=1)

        self.create_frame_options()
        self.create_frame_graph()

    def create_equalizer_tab(self):
        """Crear la pestaña del ecualizador de la interfaz"""
        if self.tab_equalizer != None:
            self.tab_equalizer.destroy()

        self.tab_equalizer = ttk.Frame(self.main_window)
        self.main_window.add(self.tab_equalizer, text="Equalizer")

        self.tab_equalizer.grid_columnconfigure(0, weight=3)
        self.tab_equalizer.grid_columnconfigure(1, weight=1)
        self.tab_equalizer.grid_rowconfigure(0, weight=3)
        self.tab_equalizer.grid_rowconfigure(1, weight=1, minsize=200)

        # >>>>> Crear el frame del ecualizador <<<<<
        self.create_frame_equalizer()
        
        # >>>>> Crear la gráfica con los niveles para el ecualizador <<<<<
        self.create_equalizer_graph()

        # >>>>> Crear el frame para graficar los datos del usuario <<<<<
        self.create_frame_user_data()

        # >>>>> Crear los sliders del ecualizador <<<<<
        self.create_equalizer_scales()

        # >>>>> Crear el frame para poner botones relacionados con la ecualización <<<<<
        self.create_frame_equalizer_options()

    def create_frame_options(self):
        """Crear el frame de opciones de la pestaña principal con scrollbar"""
        self.frm_options_outer = ttk.Frame(
            self.tab_main, padding=5, relief="groove", borderwidth=2
        )
        self.frm_options_outer.grid(row=0, column=0, sticky="nsew")
        self.frm_options_outer.grid_rowconfigure(0, weight=1)
        self.frm_options_outer.grid_columnconfigure(0, weight=1)

        self.options_canvas = tk.Canvas(self.frm_options_outer, highlightthickness=0)
        self.options_scrollbar = ttk.Scrollbar(
            self.frm_options_outer, orient="vertical", command=self.options_canvas.yview
        )
        self.frm_options = ttk.Frame(self.options_canvas)

        self.options_canvas.create_window((0, 0), window=self.frm_options, anchor="nw")
        self.options_canvas.configure(yscrollcommand=self.options_scrollbar.set)

        self.options_canvas.grid(row=0, column=0, sticky="nsew")
        self.options_scrollbar.grid(row=0, column=1, sticky="ns")

        self.frm_options.bind(
            "<Configure>",
            lambda e: self.options_canvas.configure(
                scrollregion=self.options_canvas.bbox("all")
            ),
        )

        # >>>>> Selección de ruido <<<<<
        self.create_radio_buttons_noise_type()

        # >>>>> Selección de tipo de filtro <<<<<
        self.create_radio_buttons_band_type()

        # >>>>> Selección de tipo de filtro <<<<<
        self.create_radio_buttons_filter_type()

        # >>>>> Selección de las bandas <<<<<
        self.create_combobox_bands_selector()

        # >>>>> Selección del tiempo de ruido <<<<<
        self.create_entry_noise_time()

        # Espacio en blanco antes de los botones
        ttk.Label(self.frm_options, text="").grid(row=17)

        # >>>>> Realizar el filtro <<<<<
        self.create_button_apply_filter()

        # >>>>> Reproducir y parar el ruido <<<<<
        self.create_button_play_stop_noise()
        
        # >>>>> Guardar señal filtrada en WAV <<<<<
        self.create_button_save_wav()

    def create_frame_graph(self):
        """Crear el frame del gráfico de la pestaña principal"""
        self.frm_graph = ttk.Frame(
            self.tab_main, padding=10, relief="groove", borderwidth=2
        )
        self.frm_graph.grid(row=0, column=1, sticky="nsew")
        self.frm_graph.grid_columnconfigure(0, weight=1)
        self.frm_graph.grid_rowconfigure(0, weight=1)

    def create_radio_buttons_noise_type(self):
        """Crear los radio buttons para seleccionar el tipo de ruido"""
        ttk.Label(self.frm_options, text="\nSeleccione el tipo de ruido:").grid(
            row=0, sticky="w"
        )

        # Ruido rosa
        self.radio_btn_pink = ttk.Radiobutton(
            self.frm_options,
            text="Ruido rosa",
            variable=self.noise_type,
            value="PINK NOISE",
            command=self.check_conditions,
        )
        self.radio_btn_pink.grid(row=1, sticky="w")

        # Ruido blanco
        self.radio_btn_white = ttk.Radiobutton(
            self.frm_options,
            text="Ruido blanco",
            variable=self.noise_type,
            value="WHITE NOISE",
            command=self.check_conditions,
        )
        self.radio_btn_white.grid(row=2, sticky="w")

    def create_radio_buttons_band_type(self):
        """Crear los radio buttons para seleccionar el tipo de banda"""
        ttk.Label(self.frm_options, text="\nSeleccione el tipo de banda:").grid(
            row=3, sticky="w"
        )

        self.radio_btn_octave = ttk.Radiobutton(
            self.frm_options,
            text="Octavas",
            variable=self.band_type,
            value="1/1",
            command=self.on_band_type_selected,
        )  # Crear botón para octavas
        self.radio_btn_octave.grid(row=4, sticky="w")

        self.radio_btn_third_octave = ttk.Radiobutton(
            self.frm_options,
            text="Tercios de octavas",
            variable=self.band_type,
            value="1/3",
            command=self.on_band_type_selected,
        )  # Crear botón para tercios de octavas
        self.radio_btn_third_octave.grid(row=5, sticky="w")

    def create_radio_buttons_filter_type(self):
        """Crear los radio buttons para seleccionar el tipo de filtro"""
        ttk.Label(
            self.frm_options, text="\nSeleccione el tipo de filtro:"
        ).grid(row=6, sticky="w")

        self.radio_btn_lowpass = ttk.Radiobutton(
            self.frm_options,
            text="Filtro paso bajo",
            variable=self.filter_type,
            value="low_pass",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_lowpass.grid(row=7, sticky="w")

        self.radio_btn_highpass = ttk.Radiobutton(
            self.frm_options,
            text="Filtro paso alto",
            variable=self.filter_type,
            value="high_pass",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_highpass.grid(row=8, sticky="w")

        self.radio_btn_bandpass = ttk.Radiobutton(
            self.frm_options,
            text="Filtro paso banda",
            variable=self.filter_type,
            value="band_pass",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_bandpass.grid(row=9, sticky="w")

        # self.radio_btn_notch = ttk.Radiobutton(
        #     self.frm_options,
        #     text="Filtro notch",
        #     variable=self.filter_type,
        #     value="notch",
        #     command=self.on_band_type_selected,
        #     state="disabled",
        # )
        # self.radio_btn_notch.grid(row=10, sticky="w") BORRAR

        self.radio_btn_allpass = ttk.Radiobutton(
            self.frm_options,
            text="Filtro paso todo",
            variable=self.filter_type,
            value="all_pass",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_allpass.grid(row=10, sticky="w")

    def create_combobox_bands_selector(self):
        """Crear los combobox para seleccionar las bandas"""
        ttk.Label(self.frm_options, text="").grid(row=11, sticky="w")
        ttk.Label(self.frm_options, text="Banda de corte inferior:").grid(
            row=12, column=0, sticky="w"
        )
        ttk.Label(self.frm_options, text="Banda de corte superior:").grid(
            row=12, column=1, sticky="w"
        )

        self.combo_low_freq = ttk.Combobox(
            self.frm_options, state="disabled", postcommand=self.update_bands
        )
        self.combo_low_freq.grid(row=13, column=0, sticky="w")
        self.combo_low_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        self.combo_high_freq = ttk.Combobox(
            self.frm_options, state="disabled", postcommand=self.update_bands
        )
        self.combo_high_freq.grid(row=13, column=1, sticky="w")
        self.combo_high_freq.bind("<<ComboboxSelected>>", self.check_conditions)

    def create_entry_noise_time(self):
        """Crear la entrada para introducir el tiempo de ruido"""
        ttk.Label(
            self.frm_options, text="\nDuración del ruido (segundos):"
        ).grid(row=14, columnspan=2)
        self.time_entry = ttk.Entry(self.frm_options)
        self.time_entry.grid(row=15, columnspan=2)

    def create_button_apply_filter(self):
        """Crea botón que aplica el filtro"""
        self.btn_apply_filter = ttk.Button(
            self.frm_options,
            text="APLICAR EL FILTRO",
            command=self.on_apply_filter,
            state="disabled",
        )
        self.btn_apply_filter.grid(row=16, columnspan=2)

    def create_button_play_stop_noise(self):
        """Crea los botones de PLAY y STOP para el ruido"""
        # >>>>> Botón de reproducción <<<<<
        self.btn_play_noise = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: [
                self.audio_player.start_noise_thread(
                    self.filter.filtered_signal
                ),
                self.btn_stop.config(state="!disabled"),
            ],
            state="disabled",
        )
        self.btn_play_noise.grid(row=17, columnspan=2)

        # >>>>> Botón STOP <<<<<
        self.btn_stop = ttk.Button(
            self.frm_options,
            text="STOP REPRODUCCIÓN",
            command=lambda: [
                self.audio_player.control_noise_event.set(),
                self.btn_stop.config(state="disabled"),
            ],
            state="disabled",
        )
        self.btn_stop.grid(row=18, columnspan=2)
        
    def create_button_save_wav(self):
        """Crea el botón para guardar la señal filtrada en WAV"""
        self.btn_save_wav = ttk.Button(
            self.frm_options,
            text="GUARDAR WAV",
            command=self.on_save_filtered_signal,
            state="disabled",
        )
        self.btn_save_wav.grid(row=19, columnspan=2)

    def create_frame_equalizer(self):
        """Crea el marco para el ecualizador"""
        self.frm_equalizer_graph = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=2
        )
        self.frm_equalizer_graph.grid(row=0, column=0, sticky="nsew")
        self.frm_equalizer_graph.grid_columnconfigure(0, weight=1)
        self.frm_equalizer_graph.grid_rowconfigure(0, weight=1)

    def create_frame_user_data(self):
        """Crear el marco para representar los valores promediados del usuario"""
        self.frm_user_data_menu = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=2
        )
        self.frm_user_data_menu.grid(row=0, column=1, sticky="nsew")

        ttk.Label(
            self.frm_user_data_menu,
            text="Introduza los valores promediados para cada banda:",
        ).grid(row=0, column=0)

        # Crear un Canvas y un Scrollbar dentro del Frame
        self.user_data_canvas = tk.Canvas(self.frm_user_data_menu)
        self.scrollbar = ttk.Scrollbar(
            self.frm_user_data_menu,
            orient="vertical",
            command=self.user_data_canvas.yview,
        )

        # Frame interno donde estarán los widgets
        self.frm_user_data_entries = ttk.Frame(self.user_data_canvas)
        self.frm_user_data_entries.bind(
            "<Configure>",
            lambda e: self.user_data_canvas.configure(
                scrollregion=self.user_data_canvas.bbox("all")
            ),
        )

        # Agregar el Frame al Canvas
        self.window = self.user_data_canvas.create_window(
            (0, 0), window=self.frm_user_data_entries, anchor="center"
        )

        # Ubicar Canvas y Scrollbar en la cuadrícula
        self.user_data_canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Configurar el Canvas para usar la Scrollbar
        self.user_data_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Expandir correctamente en el grid
        self.frm_user_data_menu.columnconfigure(0, weight=1)
        self.frm_user_data_menu.rowconfigure(1, weight=1)

        self.create_user_data_entry()
        self.disable_widgets(self.frm_user_data_entries)

    def create_user_data_entry(self):
        """Crea los inputs para que el usuario introduzca los valores manualmente"""
        # Limpio el diccionario por si acaso
        self.user_data_entry_vars.clear()
        self.user_data_entry_dict.clear()

        # Registro de validación
        validate_input = self.root.register(self.on_validate_user_data_input)

        # Crear etiquetas y entradas para cada frecuencia nominal seleccionada
        for row, freq in enumerate(self.filter.selected_nominal_frequencies):
            ttk.Label(self.frm_user_data_entries, text=f"{freq}Hz = ").grid(
                row=row, column=0, sticky="nsew"
            )  # Etiqueta para la frecuencia

            # Se crea un StringVar para la frecuencia
            var = tk.StringVar()
            self.user_data_entry_vars[freq] = var  # Guardarlo en el diccionario

            # Crear un Entry para la frecuencia con validación
            entry = ttk.Entry(
                self.frm_user_data_entries,
                textvariable=var,
                validate="key",
                validatecommand=(validate_input, "%P"),
            )
            entry.grid(row=row, column=1)

            entry.insert(0, "0")  # Valor por defecto

            ttk.Label(self.frm_user_data_entries, text="dB").grid(
                row=row, column=2
            )
            
            self.user_data_entry_dict[freq] = entry

    def create_frame_equalizer_options(self):
        """Crea las opciones para oder ecualizar"""
        self.frm_equalizer_options = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=4
        )
        self.frm_equalizer_options.grid(row=1, column=1, sticky="nsew")

        # >>>> Aplanar los controles de ganancia <<<<<
        self.btn_reset_scales = ttk.Button(
            self.frm_equalizer_options,
            text="Aplanar los controles de ganancia",
            command=self.reset_scales,
        )
        self.btn_reset_scales.grid(row=0, column=0)

        # >>>> Aplicar ecualización <<<<<
        self.btn_apply_equalization = ttk.Button(
            self.frm_equalizer_options,
            text="Aplicar ecualización",
            command=self.on_apply_equalization,
        )
        self.btn_apply_equalization.grid(row=1, column=0)

        # >>>> Introducir valores promediados en el recinto fuente manualmente <<<<
        self.btn_introduce_user_data = ttk.Button(
            self.frm_equalizer_options,
            text="Introducir datos manualmente",
            command=lambda: [
                self.enable_widgets(self.frm_user_data_entries),
                self.btn_apply_user_data.config(state="!disabled"),
            ],
        )
        self.btn_introduce_user_data.grid(row=2, column=0)

        self.btn_apply_user_data = ttk.Button(
            self.frm_equalizer_options,
            text="Aplicar valores introducidos",
            command=self.on_apply_user_data,
            state="disabled",
        )
        self.btn_apply_user_data.grid(row=2, column=1)

        # >>>> Introducir valores promediados en el recinto fuente manualmente <<<<
        self.btn_introduce_csv = ttk.Button(
            self.frm_equalizer_options,
            text="Introducir datos .csv",
            command=lambda: [
                self.read_csv_data(),
                self.disable_widgets(self.frm_user_data_entries),
                self.check_energy_averaging_iso_16283_1()
            ],
        )
        self.btn_introduce_csv.grid(row=3, column=0)
        
        self.btn_csv_info = ttk.Button(
            self.frm_equalizer_options,
            text="[?] Información sobre .csv",
            command=self.on_show_csv_info,
        )
        self.btn_csv_info.grid(row=3, column=1, sticky="w")

    def create_equalizer_scales(self):
        """Crea la interfaz con los botones delizables para ecualizar la señal"""
        self.frm_equalizer_scales = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=2
        )
        self.frm_equalizer_scales.grid(row=1, column=0, sticky="nsew")

        self.clear_frame(self.frm_equalizer_scales)
        self.frm_equalizer_scales.grid_columnconfigure(0, weight=1)
        self.frm_equalizer_scales.grid_rowconfigure(0, weight=1)

        # Crear canvas con barra de desplazamiento para evitar desbordamiento en la pantalla
        self.scales_canvas = tk.Canvas(self.frm_equalizer_scales, highlightthickness=0)
        self.scales_scrollbar = tk.Scrollbar(
            self.frm_equalizer_scales,
            orient="horizontal",
            command=self.scales_canvas.xview,
        )

        # Sincronizar Canvas con la barra de desplazamiento
        self.scales_canvas.config(xscrollcommand=self.scales_scrollbar.set)

        # Se colocan el Canvas y la barra de desplazamiento
        self.scales_canvas.grid(row=0, column=0, sticky="nsew")
        self.scales_scrollbar.grid(row=1, column=0, sticky="ew")

        # Crear un Frame dentro del scales_canvas para colocar los sliders
        self.frm_scales = tk.Frame(
            self.scales_canvas, relief="raised", borderwidth=5
        )
        self.scales_canvas.create_window(
            (0, 0), window=self.frm_scales, anchor="nw"
        )

        self.equalizer_scales = []  # Reiniciar array con los controles de ganancia
        self.equalizer_scales_labels = (
            []
        )  # Reiniciar etiquetas para evitar duplicados

        # Formatear la salida para evitar ".0" en enteros
        formatted_frequencies = [
            int(f) if f.is_integer() else f
            for f in self.filter.selected_nominal_frequencies
        ]

        self.update_scales_values_and_labels(formatted_frequencies)

        # Actualizar el área desplazable (scrollable region)
        self.frm_scales.update_idletasks()  # Actualiza la interfaz antes de ajustar el área desplazable
        self.scales_canvas.config(
            scrollregion=self.scales_canvas.bbox("all")
        )  # Indica la región desplazable del Canvas, en este caso todo el Canvas
        self.scales_canvas.config(height=250)

    def update_scales_values_and_labels(self, formatted_frequencies):
        """Actualiza los valores de los controles de ganancia y las frecuencias a las que pertenecen"""
        for i, freq in enumerate(formatted_frequencies):
            label_var = tk.StringVar(value="0.0 dB")

            freq_label = ttk.Label(self.frm_scales, text=f"{freq} Hz")
            freq_label.grid(row=0, column=i)

            freq_scale = ttk.Scale(
                self.frm_scales,
                from_=10,
                to=-10,
                orient="vertical",
                length=150,
                command=lambda value, var=label_var: self.update_scales_gain(
                    float(value), var
                ),  # Enlazar cada slider con su propia etiqueta
            )
            freq_scale.grid(row=1, column=i)

            scale_label = ttk.Label(
                self.frm_scales,
                textvariable=label_var,
                width=8,  # Fijar un ancho fijo -> Tamaño máximo del texto "-xx.x_dB"
                anchor="center",  # Texto etiqueta centrado
            )
            scale_label.grid(row=2, column=i)

            self.equalizer_scales_labels.append(scale_label)
            self.equalizer_scales.append(freq_scale)

    def reset_scales(self):
        for scale in self.equalizer_scales:
            scale.set(0)

    def create_main_graph(self):
        """Crea el gráfico de la pestaña principal (sin ajustes de ecualización)"""
        # Elimina la instancia si existe
        if self.main_graph:
            del self.main_graph

        self.main_graph = FilterPlotter(self.filter)
        self.main_graph.plot_filtered_signal_levels()
        self.main_graph.create_annotation_to_show_levels()

        self.plot_canvas_main_graph = FigureCanvasTkAgg(
            self.main_graph.figure, self.frm_graph
        )

        self.plot_canvas_main_graph.draw()
        self.plot_canvas_main_graph.get_tk_widget().grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )  # Mostrar el lienzo en la ventana

        # Conectar el evento de movimiento del ratón a la función
        self.plot_canvas_main_graph.mpl_connect(
            "motion_notify_event",
            lambda event: self.main_graph.on_hover(
                event, plot_canvas=self.plot_canvas_main_graph
            ),
        )

    def create_equalizer_graph(self):
        """Representa la señal en dB en la pestaña de ecualización"""
        # Elimina la instancia si existe
        if self.equalizer_graph:
            del self.equalizer_graph

        self.equalizer_graph = FilterPlotter(self.filter)
        self.equalizer_graph.plot_filtered_signal_levels()
        self.equalizer_graph.create_scatter_points()
        self.equalizer_graph.create_annotation_to_show_levels()

        self.plot_canvas_equalizer_graph = FigureCanvasTkAgg(
            self.equalizer_graph.figure, self.frm_equalizer_graph
        )

        self.plot_canvas_equalizer_graph.draw()
        self.plot_canvas_equalizer_graph.get_tk_widget().grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )  # Mostrar el lienzo en la ventana

        # Conectar el evento de movimiento del ratón a la función
        self.plot_canvas_equalizer_graph.mpl_connect(
            "motion_notify_event",
            lambda event: self.equalizer_graph.on_hover(
                event, plot_canvas=self.plot_canvas_equalizer_graph
            ),
        )

    def update_scales_gain(self, value, label_var):
        """Actualiza la etiqueta del deslizador correspondiente y
        superpone en la gráfica la ganancia aplicada
        """
        label_var.set(f"{float(value):.1f} dB")
        self.update_equalized_plot_points()

    def update_equalized_plot_points(self):
        """Actualiza los puntos rojos en el gráfico según los valores de los sliders"""
        # Obtener los valores actuales de los sliders
        new_levels = [scale.get() for scale in self.equalizer_scales]

        # Sumar los valores de los sliders a los niveles originales
        equalized_levels = np.array(
            self.filter.filtered_bands_levels
        ) + np.array(new_levels)

        # Actualizar la posición de los puntos en la gráfica
        # Generar matriz de coordenadas X (frecuencia) e Y (niveles ecualizazdos) para cada punto
        self.equalizer_graph.scatter_points.set_offsets(
            np.c_[self.filter.fm_selected_bands, equalized_levels]
        )

        # Eliminar la línea anterior si existe
        if hasattr(self, "spline_line"):
            self.spline_line.remove()

        # Redibujar el gráfico con los nuevos valores
        self.plot_canvas_equalizer_graph.draw_idle()  # actualiza la gráfica sin bloquear la interfaz.

    def on_band_type_selected(self):
        """Aplica todo cuando se selecciona un radio button de tipo de banda"""
        self.btn_apply_filter.config(state="disabled")

        self.radio_btn_lowpass.config(state="!disabled")
        self.radio_btn_highpass.config(state="!disabled")
        self.radio_btn_bandpass.config(state="!disabled")
        self.radio_btn_allpass.config(state="!disabled")

        self.clear_bands()
        self.update_bands()
        self.check_conditions()

    def clear_bands(self):
        """Limpiar las bandas seleccionadas"""
        self.combo_low_freq.set("")
        self.combo_high_freq.set("")

    def get_bands_for_band_type(self):
        """Obtener las bandas disponibles para el tipo de banda seleccionado"""
        if self.band_type.get() == "1/1":
            bands = NOMINAL_OCTAVE_FREQ
        elif self.band_type.get() == "1/3":
            bands = NOMINAL_THIRDOCTAVE_FREQ

        return bands

    def update_bands(self):
        """Actualizar las bandas disponibles en el combobox"""
        # Obtener bandas nominales y frecuencias de corte marcadas
        bands = self.get_bands_for_band_type()
        selected_fl = self.combo_low_freq.get()
        selected_fh = self.combo_high_freq.get()

        # Obtener el tipo de fitlro seleccionado
        filter_type = self.filter_type.get()

        if filter_type != "":
            # Activar desplegables para seleccionar bandas
            self.combo_low_freq.config(state="readonly")
            self.combo_high_freq.config(state="readonly")

            match filter_type:
                case "low_pass":
                    self.combo_low_freq.set(bands[0])
                    self.combo_low_freq.config(state="disabled")
                    self.combo_high_freq["values"] = bands

                case "high_pass":
                    self.combo_high_freq.set(bands[-1])
                    self.combo_high_freq.config(state="disabled")
                    self.combo_low_freq["values"] = bands

                case "band_pass":
                    self.update_bandpass_bands(bands, selected_fl, selected_fh)

                # case "notch":
                #     self.update_bandpass_bands(bands, selected_fl, selected_fh) BORRAR

                case "all_pass":
                    self.combo_low_freq.set(bands[0])
                    self.combo_low_freq.config(state="disabled")
                    self.combo_high_freq.set(bands[-1])
                    self.combo_high_freq.config(state="disabled")

    def update_bandpass_bands(self, bands, selected_fl, selected_fh):
        """Actualizar las bandas disponibles para el filtro paso banda"""
        if selected_fl == "" and selected_fh == "":  # Ninguna seleccionada
            self.combo_low_freq["values"] = bands
            self.combo_high_freq["values"] = bands

        elif selected_fl != "" and selected_fh != "":  # Una de las dos
            self.combo_high_freq["values"] = bands[
                bands.index(float(selected_fl)) :
            ]
            self.combo_low_freq["values"] = bands[
                : bands.index(float(selected_fh)) + 1
            ]

        # Ambas seleccionadas
        if selected_fl != "":
            self.combo_high_freq["values"] = bands[
                bands.index(float(selected_fl)) :
            ]
        elif selected_fh != "":
            self.combo_low_freq["values"] = bands[
                : bands.index(float(selected_fh)) + 1
            ]

    def delete_and_change_entry_value(
        self, entry, value, initial_pos=0, final_pos=tk.END
    ):
        """Eliminar el contenido de un entry y cambiarlo por otro"""
        entry.delete(initial_pos, final_pos)
        entry.insert(initial_pos, value)

    def check_selected_time_type(self):
        """Comprobar el tipo de los segundos elegidos"""
        try:
            float(
                self.time_entry.get()
            )  # Obtengo el valor de tiempo introducido e intento convertirlo a float
        except:
            match self.time_entry.get():
                case "":
                    messagebox.showinfo(
                        "INFORMACIÓN",
                        f"Como no se ha introducido ninguna duración se establece por defecto {DURATION} segundos",
                    )
                    self.delete_and_change_entry_value(
                        self.time_entry, DURATION
                    )
                case _:
                    messagebox.showerror(
                        "ERROR",
                        f"La duración introducida no sigue ningún formato válido, introduzca un número o deje en blanco para valor por defecto ({DURATION})",
                    )
        else:
            self.check_measurement_time_iso_16283_1()

    def check_measurement_time_iso_16283_1(self):
        """Gestiona según las bandas a medir y el tiempo seleccionado si se cumple la norma ISO 16283-1:2014"""
        time_entry = float(self.time_entry.get())  # Tiempo introducido por el usuario
        fl = float(self.combo_low_freq.get())  # Frecuencia de corte inferior

        # Se comprueba la frecuencia de corte inferior para determinar el tiempo requerido
        if fl >= 500:
            required_time = 4
        elif 100 <= fl <= 400:
            required_time = 6
        elif fl <= 80:
            required_time = 15

        # Se comprueba se el tiempo introducido es menor al requerido por la norma
        if time_entry < required_time:
            self.delete_and_change_entry_value(self.time_entry, required_time)
            messagebox.showwarning(
                "ADVERTENCIA",
                f"Se ha cambiado automaticamente la duración a {required_time} ya que con la duración introducida no se cumplía la norma ISO 16283-1:2014",
            )
        else:
            if time_entry != int(
                time_entry
            ):  # Tipo float introducido -> cambio a int
                self.delete_and_change_entry_value(
                    self.time_entry, int(time_entry)
                )
                messagebox.showwarning(
                    "ADVERTENCIA",
                    f"Se ha cambiado automaticamente la duración a {self.time_entry.get()} segundos por haber introducido un valor decimal",
                )

    def check_energy_averaging_iso_16283_1(self):
        """ Verificar si se cumple el requisito de no superar los 8dB en bandas de tercio de octava adyacentes """
        average_energy_levels = []

        for level in self.user_data_entry_vars.values():
            # Si el valor no se puede convertir a float, se asigna 0.0
            try:
                value = float(level.get())
            except (ValueError, TypeError):
                value = 0.0  # Si no se puede convertir a float, asignar un valor por defecto (0.0)
                level.set(str(value))  # Actualizar el Entry con el valor por defecto
            average_energy_levels.append(value)

        for idx, freq in enumerate(self.user_data_entry_vars.keys()):
            self.user_data_entry_dict[freq].configure(foreground="black")

            if idx == 0:
                """ Primera banda """
                level = float(average_energy_levels[idx])
                next_level = float(average_energy_levels[idx+1])

                if abs(next_level - level) > 8:
                    print(f"ERROR en banda de {freq} Hz")
                    self.user_data_entry_dict[freq].configure(foreground="red")
                
            elif idx == len(average_energy_levels)-1:
                """ Última banda """
                prev_level = float(average_energy_levels[idx-1])
                level = float(average_energy_levels[idx])

                if abs(level - prev_level) > 8:
                    print(f"ERROR en banda de {freq} Hz")
                    self.user_data_entry_dict[freq].configure(foreground="red")

            else:
                """ Resto de bandas """
                prev_level = float(average_energy_levels[idx-1])
                level = float(average_energy_levels[idx])
                next_level = float(average_energy_levels[idx+1])

                if abs(level - prev_level) > 8 or abs(next_level-level) > 8:
                    print(f"ERROR en banda de {freq} Hz")
                    self.user_data_entry_dict[freq].configure(foreground="red")

    def check_conditions(self, event=None):
        """Comprueba si se puede activar el botón de filtrado"""
        if all(
            [
                self.noise_type.get() != "",
                self.band_type.get() != "",
                self.combo_low_freq.get() != "",
                self.combo_high_freq.get() != "",
            ]
        ):
            self.btn_apply_filter.config(state="normal")

    def apply_filter(self):
        """Aplicar el filtro seleccionado al tipo de ruido seleccionado"""
        try:
            # Verificar si la ventana principal está activa antes de continuar
            if not self.root.winfo_exists():
                return
        except TclError:
            # La ventana principal ha sido destruida
            return

        self.filter.signal = self.noise_generator.generate_pink_noise(
            duration=60
        )
        self.filter.octave_filter()

        # Si el hilo de reproducción está activo se detiene
        self.audio_player.stop_noise_thread()

        try:
            # Obtiene la duración introducida para el audio (por defecto duración en config.py)
            time_entry = int(self.time_entry.get())

            # Obtener valores de la variable actual del ruido y del tipo de filtro
            selected_noise = self.noise_type.get()
            selected_filter = self.band_type.get()
            bandas_a_filtrar = [
                float(self.combo_low_freq.get()),
                float(self.combo_high_freq.get()),
            ]
        except:
            # Verificar si la ventana principal está activa antes de mostrar el mensaje de error
            if self.root.winfo_exists():
                # Muestra ventana de error si no hay ruido y/o filtro seleccionado
                messagebox.showerror(
                    "Advertencia",
                    "No se ha podido realizar el filtrado de la señal de referencia, revise el tipo de filtro, de ruido, bandas a filtrar y duración",
                )
        else:
            from config import SAMPLE_RATE
            
            # Para evitar transitorios de filtros de alto orden (como orden 32), 
            # se generam un periodo extra de "warmup" y luego lo descartamos tras el filtrado.
            warmup_time = 1  # 1 segundo de "calentamiento" para el filtro
            total_duration = time_entry + warmup_time

            # Decidir tipo de filtro y de ruido para filtrar
            if selected_noise == "WHITE NOISE":  # RUIDO BLANCO
                self.filter.signal = self.noise_generator.generate_white_noise(
                    total_duration
                )
            elif selected_noise == "PINK NOISE":  # RUIDO ROSA
                self.filter.signal = self.noise_generator.generate_pink_noise(
                    total_duration
                )

            if selected_filter == "1/1":  # 1/1 OCTAVA
                self.filter.octave_filter(bandas_a_filtrar)
            elif selected_filter == "1/3":  # 1/3 OCTAVA
                self.filter.third_octave_filter(bandas_a_filtrar)

            # Descartar el periodo de warmup para eliminar el transitorio del filtro
            warmup_samples = int(warmup_time * SAMPLE_RATE)
            self.filter.signal = self.filter.signal[warmup_samples:]
            self.filter.filtered_signal = self.filter.filtered_signal[warmup_samples:]
            if self.filter.filtered_bands is not None:
                self.filter.filtered_bands = self.filter.filtered_bands[:, warmup_samples:]

            self.filter.get_selected_nominal_frequencies()

    def read_csv_data(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if archivo:
            try:
                with open(archivo, newline="", encoding="utf-8") as f:
                    lector = csv.reader(f, delimiter=";")
                    datos = list(lector)  # Convertir a lista

                if len(datos) < 2:
                    raise ValueError("El archivo no tiene el formato esperado (mínimo dos filas).")

                # Validar valores de dB antes de convertirlos
                for level_str in datos[1]:
                    if not self.is_valid_db_string(level_str):
                        messagebox.showerror(
                            "ERROR DE FORMATO",
                            f"El valor '{level_str}' en el archivo CSV no es válido.\n\n"
                            "Los valores aceptados deben cumplir:\n"
                            "- Máximo 3 dígitos enteros.\n"
                            "- Máximo 2 dígitos decimales.\n"
                            "- Signo negativo opcional al inicio.\n"
                            "- Punto (.) como separador decimal"
                        )
                        return

                csv_frequencies = np.array([float(f) for f in datos[0]])
                csv_band_levels = np.array([float(l) for l in datos[1]])

                if np.array_equal(
                    self.filter.selected_nominal_frequencies, csv_frequencies
                ):
                    for csv_level, entry_var in zip(
                        csv_band_levels, self.user_data_entry_vars.values()
                    ):
                        # Formatear para evitar muchos decimales innecesarios en la UI
                        entry_var.set(f"{csv_level:.2f}".rstrip('0').rstrip('.'))

                    self.root.update_idletasks()
                else:
                    messagebox.showerror(
                        "ERROR",
                        f"Las frecuencias del archivo con las medidas promediadas no coinciden con las frecuencias filtradas",
                    )
            except Exception as e:
                messagebox.showerror("ERROR", f"No se pudo leer el archivo CSV: {e}")


    def on_apply_filter(self):
        """ Aplicar filtro """
        
        # Mensaje pop-up indicando si se quiere realizar otro filtrado, ya que existe una señal ya creada
        if self.filter.filtered_signal is not None:
            confirm = messagebox.askyesno(
                "Confirmación",
                "Ya existe una señal generada. ¿Estás seguro de que quieres generar una nueva señal? Se perderá la ecualización anterior.",
            )
            if not confirm:
                return
                
        self.check_selected_time_type()
        self.apply_filter()
        self.create_main_graph()
        self.create_equalizer_tab()
        self.check_conditions()
        self.btn_play_noise.config(state="!disabled")
        self.btn_save_wav.config(state="!disabled")

    def on_apply_equalization(self):
        """ Aplicar ecualización """
        print("Se aplica la ecualización")
        # Si el hilo de reproducción está activo se detiene
        self.audio_player.stop_noise_thread()
        
        self.btn_apply_equalization.config(state="disabled")
        scales_gain_db = np.array(
            [scale.get() for scale in self.equalizer_scales]
        )
        self.filter.equalize_signal(scales_gain_db)
        self.create_main_graph()
        self.create_equalizer_graph()
        self.reset_scales()

    def on_apply_user_data(self):
        """ Introducir datos del usuario """
        self.check_energy_averaging_iso_16283_1()

    def on_show_csv_info(self):
        """ Mostrar información sobre el formato del archivo CSV """
        mensaje = (
            "El archivo .csv debe tener el siguiente formato:\n\n"
            "- Primera fila: Frecuencias nominales separadas por ';'\n"
            "- Segunda fila: Niveles en dB de cada banda separados por ';'\n\n"
            "Ejemplo de contenido del archivo:\n"
            "31.5;40;50;63;80;100;125;160\n"
            "67;89;-45;12.12;14.6;75.2;78.5;80.1"
        )
        messagebox.showinfo("Información de formato CSV", mensaje)

    
    def on_close_app(self):
        """Función que se ejecuta al cerrar la ventana"""
        print("Cerrando la aplicación...")
        self.root.destroy()  # Cierra la ventana
        exit(0)  # Termina el script correctamente
        
    def get_output_data_dir(self):
        """
        Devuelve la carpeta data donde se guardarán los WAV.
        
        - Si la app se ejecuta como .exe, usa una carpeta 'data' junto al ejecutable.
        - Si se ejecuta como script .py, usa la carpeta 'data' del proyecto.
        """
        if getattr(sys, "frozen", False):
            # Ejecutándose como .exe
            base_dir = Path(sys.executable).resolve().parent
        else:
            # Ejecutándose como script
            script_dir = Path(__file__).resolve().parent
            base_dir = script_dir.parent.parent  # subir hasta TFG_SAMUEL

        data_dir = base_dir / "data"  # Carpeta 'data' para guardar los WAV
        data_dir.mkdir(parents=True, exist_ok=True)  # Crear la carpeta 'data' si no existe
        return data_dir


    def build_output_filename(self):
        """
        Construye un nombre de archivo informativo para la señal filtrada.
        """
        noise_type = self.noise_type.get().strip().replace(" ", "_").lower()
        band_type = self.band_type.get().strip().replace("/", "-")
        low_freq = self.combo_low_freq.get().strip()
        high_freq = self.combo_high_freq.get().strip()
        duration = self.time_entry.get().strip()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return (
            f"filtered_{noise_type}_{band_type}_"
            f"{low_freq}_{high_freq}_{duration}s_{timestamp}.wav"
        )


    def save_signal_to_wav(self, signal, output_path):
        """
        Guarda una señal mono en formato WAV PCM de 16 bits.
        """
        # Para guardar la señal en formato WAV PCM de 16 bits es necesario escalarla al rango de -32768 a 32767
        signal_to_save = np.clip(signal, -32768, 32767).astype(np.int16)  

        # Guardar la señal en un archivo WAV
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16 bits = 2 bytes
            wav_file.setframerate(SAMPLE_RATE)  # Frecuencia de muestreo
            wav_file.writeframes(signal_to_save.tobytes())  # Escribir los datos de audio


    def on_save_filtered_signal(self):
        """
        Guarda la señal filtrada actual en la carpeta data.
        """
        if self.filter.filtered_signal is None:
            messagebox.showwarning(
                "ADVERTENCIA",
                "No hay ninguna señal filtrada para guardar."
            )
            return

        try:
            data_dir = self.get_output_data_dir()  # Obtener la carpeta de salida para los archivos WAV
            filename = self.build_output_filename()  # Construir un nombre de archivo informativo
            output_path = data_dir / filename  # Ruta completa del archivo de salida

            self.save_signal_to_wav(self.filter.filtered_signal, output_path)  # Guardar la señal filtrada en formato WAV

            messagebox.showinfo(
                "GUARDADO CORRECTO",
                f"Se ha guardado la señal filtrada en:\n{output_path}"
            )

        except Exception as e:
            messagebox.showerror(
                "ERROR",
                f"No se pudo guardar el archivo WAV:\n{e}"
            )
