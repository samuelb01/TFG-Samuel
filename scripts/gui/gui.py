from noise_generator.noise_generator import NoiseGenerator
from filter.filter import Filter
from audio_player.audio_player import AudioPlayer
from filter_plotter.filter_plotter import FilterPlotter

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import TclError

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import NOMINAL_OCTAVE_FREQ, NOMINAL_THIRDOCTAVE_FREQ, DURATION


class GUI:
    def __init__(self):
        """Constructor de la clase GUI"""
        self.noise_generator = NoiseGenerator()
        self.filter = Filter()
        self.audio_player = AudioPlayer()

        self.main_graph = None
        self.equalizer_graph = None

        self.root = tk.Tk()
        self.root.title("PROYECTO SAMUEL")
        self.root.state("zoomed")  # Pantalla completa

        self.computer_screen_width = self.root.winfo_screenwidth()
        self.computer_screen_height = self.root.winfo_screenheight()

        self.main_window = ttk.Notebook(self.root)  # Ventana principal

        self.noise_type = tk.StringVar()
        self.band_type = tk.StringVar()
        self.filter_type = tk.StringVar()

        self.create_main_tab()
        # self.create_equalizer_tab()

        # # 85% del ancho de la pantalla para el gráfico y el 15% para el menú de opciones
        # self.tab_main.grid_columnconfigure(1, weight=85)
        # self.tab_main.grid_columnconfigure(0, weight=15)

        self.main_window.grid()
        self.root.mainloop()

    def create_main_tab(self):
        """Crear la pestaña principal de la interfaz"""
        self.tab_main = ttk.Frame(self.main_window)
        self.main_window.add(self.tab_main, text="Main")

        self.create_frame_options()
        self.create_frame_graph()

    def create_equalizer_tab(self):
        """Crear la pestaña del ecualizador de la interfaz"""
        self.tab_equalizer = ttk.Frame(self.main_window)
        self.main_window.add(self.tab_equalizer, text="Equalizer")

        # >>>>> Crear el frame del ecualizador <<<<<
        self.create_frame_equalizer()

        # >>>>> Crear la gráfica con los niveles para el ecualizador <<<<<
        self.create_equalizer_graph()

        # >>>>> Crear los sliders del ecualizador <<<<<
        self.create_scales_equalizer()

    def create_frame_options(self):
        """Crear el frame de opciones de la pestaña principal"""
        self.frm_options = ttk.Frame(
            self.tab_main, padding=10, relief="groove", borderwidth=2
        )
        self.frm_options.grid(row=0, column=0, sticky="nsew")
        self.frm_options.grid_propagate(False)

        self.frm_options.update_idletasks()
        self.frm_options.config(
            width=self.computer_screen_width * 0.25,
            height=self.computer_screen_height * 0.75,
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

    def create_frame_graph(self):
        """Crear el frame del gráfico de la pestaña principal"""
        self.frm_graph = ttk.Frame(
            self.tab_main, padding=10, relief="groove", borderwidth=2
        )
        self.frm_graph.grid(row=0, column=1, sticky="nsew")
        self.frm_graph.grid_propagate(False)

        self.frm_graph.update_idletasks()
        self.frm_graph.config(
            width=self.computer_screen_width * 0.85,
            height=self.computer_screen_height * 0.85,
        )

        # self.create_main_graph(self.frm_graph)

        # self.create_graph()

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

        self.radio_btn_notch = ttk.Radiobutton(
            self.frm_options,
            text="Filtro notch",
            variable=self.filter_type,
            value="notch",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_notch.grid(row=10, sticky="w")

        self.radio_btn_allpass = ttk.Radiobutton(
            self.frm_options,
            text="Filtro paso todo",
            variable=self.filter_type,
            value="all_pass",
            command=self.on_band_type_selected,
            state="disabled",
        )
        self.radio_btn_allpass.grid(row=11, sticky="w")

    def create_combobox_bands_selector(self):
        """Crear los combobox para seleccionar las bandas"""
        ttk.Label(self.frm_options, text="").grid(row=12, sticky="w")
        ttk.Label(self.frm_options, text="Banda de corte inferior:").grid(
            row=13, column=0, sticky="w"
        )
        ttk.Label(self.frm_options, text="Banda de corte superior:").grid(
            row=13, column=1, sticky="w"
        )

        self.combo_low_freq = ttk.Combobox(
            self.frm_options, state="disabled", postcommand=self.update_bands
        )
        self.combo_low_freq.grid(row=14, column=0, sticky="w")
        self.combo_low_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        self.combo_high_freq = ttk.Combobox(
            self.frm_options, state="disabled", postcommand=self.update_bands
        )
        self.combo_high_freq.grid(row=14, column=1, sticky="w")
        self.combo_high_freq.bind("<<ComboboxSelected>>", self.check_conditions)

    def create_entry_noise_time(self):
        """Crear la entrada para introducir el tiempo de ruido"""
        ttk.Label(
            self.frm_options, text="\nDuración del ruido (segundos):"
        ).grid(row=15, columnspan=2)
        self.time_entry = ttk.Entry(self.frm_options)
        self.time_entry.grid(row=16, columnspan=2)

    def create_button_apply_filter(self):
        self.btn_apply_filter = ttk.Button(
            self.frm_options,
            text="APLICAR EL FILTRO",
            command=lambda: [
                self.check_selected_time_type(),
                self.apply_filter(),
                self.create_main_graph(),
                self.create_equalizer_tab(),
                self.check_conditions(),
                self.btn_play_noise.config(state="!disabled"),
            ],
            state="disabled",
        )
        self.btn_apply_filter.grid(row=18, columnspan=2)

    def create_button_play_stop_noise(self):
        # >>>>> Botón de reproducción <<<<<
        self.btn_play_noise = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: [
                self.audio_player.start_noise_thread(self.filtered_noise),
                self.btn_stop.config(state="!disabled"),
            ],
            state="disabled",
        )
        self.btn_play_noise.grid(row=19, columnspan=2)

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
        self.btn_stop.grid(row=20, columnspan=2)

    def create_frame_equalizer(self):
        self.frm_equalizer_graph = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=2
        )
        self.frm_equalizer_graph.grid(row=0, column=0, sticky="nsew")

    def create_scales_equalizer(self):
        self.frm_equalizer_scales = ttk.Frame(
            self.tab_equalizer, relief="groove", borderwidth=2
        )
        self.frm_equalizer_scales.grid(row=1, column=0, sticky="nsew")

    def create_main_graph(self):
        self.main_graph = FilterPlotter(self.filter)
        self.main_graph.plot_filtered_signal_levels()
        self.main_graph.create_annotation_to_show_levels()

        self.plot_canvas_main_graph = FigureCanvasTkAgg(
            self.main_graph.figure, self.frm_graph
        )

        self.plot_canvas_main_graph.draw()
        self.plot_canvas_main_graph.get_tk_widget().grid(
            row=0, column=0, padx=10, pady=10
        )  # Mostrar el lienzo en la ventana

        # Conectar el evento de movimiento del ratón a la función
        self.plot_canvas_main_graph.mpl_connect(
            "motion_notify_event",
            lambda event: self.main_graph.on_hover(event, plot_canvas=self.plot_canvas_main_graph)
        )

    def create_equalizer_graph(self):
        self.equalizer_graph = FilterPlotter(self.filter)
        self.equalizer_graph.plot_filtered_signal_levels()
        self.equalizer_graph.create_scatter_points()
        self.equalizer_graph.create_annotation_to_show_levels()

        self.plot_canvas_equalizer_graph = FigureCanvasTkAgg(
            self.equalizer_graph.figure, self.frm_equalizer_graph
        )

        self.plot_canvas_equalizer_graph.draw()
        self.plot_canvas_equalizer_graph.get_tk_widget().grid(
            row=0, column=0, padx=10, pady=10
        )  # Mostrar el lienzo en la ventana

        # Conectar el evento de movimiento del ratón a la función
        self.plot_canvas_equalizer_graph.mpl_connect(
            "motion_notify_event",
            lambda event: self.equalizer_graph.on_hover(event, plot_canvas=self.plot_canvas_equalizer_graph)
        )

    def on_band_type_selected(self):
        """Aplica todo cuando se selecciona un radio button de tipo de banda"""
        self.btn_apply_filter.config(state="disabled")

        self.radio_btn_lowpass.config(state="!disabled")
        self.radio_btn_highpass.config(state="!disabled")
        self.radio_btn_bandpass.config(state="!disabled")
        self.radio_btn_notch.config(state="!disabled")
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

                case "notch":
                    self.update_bandpass_bands(bands, selected_fl, selected_fh)

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
        time_entry = float(self.time_entry.get())
        fl = float(self.combo_low_freq.get())

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
            # Decidir tipo de filtro y de ruido para filtrar
            if selected_noise == "WHITE NOISE":  # RUIDO BLANCO
                self.filter.signal = self.noise_generator.generate_white_noise(
                    time_entry
                )

            elif selected_noise == "PINK NOISE":  # RUIDO ROSA
                self.filter.signal = self.noise_generator.generate_pink_noise(
                    time_entry
                )

            if selected_filter == "1/1":  # 1/1 OCTAVA
                (
                    self.filtered_noise,
                    self.band_levels,
                    self.fm,
                    self.fl_selected_bands,
                    self.fm_selected_bands,
                    self.fh_selected_bands,
                ) = self.filter.octave_filter(bandas_a_filtrar)

            elif selected_filter == "1/3":  # 1/3 OCTAVA
                (
                    self.filtered_noise,
                    self.band_levels,
                    self.fm,
                    self.fl_selected_bands,
                    self.fm_selected_bands,
                    self.fh_selected_bands,
                ) = self.filter.third_octave_filter(bandas_a_filtrar)

            # self.filter.plot_filtered_signal_levels()
            # self.create_equalizer_gui()
            # self.create_equalizer_gui_buttons()
