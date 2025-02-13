# Autor: Samuel Bellón Elipe

import tkinter as tk
from tkinter import ttk, messagebox

import pyaudio
import threading

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importar constantes a usar
from config import (
    DURATION,
    SAMPLE_RATE,
    NOMINAL_OCTAVE_FREC,
    NOMINAL_THIRDOCTAVE_FREC,
)

from filters4 import (
    thirdOctaveFilter,
    octaveFilter,
)  # Importar las funciones necesarias
from noise_generator import (
    generate_white_noise,
    generate_pink_noise,
)  # Importar funciones para crear ruidos


class App:
    def __init__(self):

        # Configuración principal de la ventana
        self.root = tk.Tk()  # Ventana principal de la interfaz
        self.root.title("Ecualizador Gráfico")  # Título de la ventana
        self.root.geometry("1200x600")  # Tamaño de la ventana

        # crea las variables de control de la interfaz
        self.init_widget_types()

        # Variables de control (hilos de ejecución)
        self.noise_thread = None
        self.control_noise_event = threading.Event()

        # Variables una vez filtrado
        self.filtered_noise = None
        self.band_levels = None
        self.fm = None
        self.fl_selected_bands = None
        self.fh_selected_bands = None

        # Crea la interfaz de la app y la inicializa
        self.create_widgets()
        self.root.mainloop()

    def activate_filter_buttons(self):
        """Activa los desplegables de la interfaz para las bandas"""
        self.combo_high_freq.state(["!disabled"])
        self.combo_low_freq.state(["!disabled"])

    def delete_and_change_entry_value(self, entry, value, initial_pos=0, final_pos=tk.END):
        entry.delete(initial_pos,final_pos)
        entry.insert(initial_pos, value)

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
            self.btn_apply_filter.state(["!disabled"])

    def check_medition_time_iso_16283_1(self):
        """Gestiona según las bandas a medir y el tiempo seleccionado si se cumple la norma ISO 16283-1:2014"""
        time_entry = float(self.time_entry.get())
        fl = float(self.combo_low_freq.get())
        # fh = self.combo_high_freq.get()

        # if fl <= 50 and fh <= 80:
        #     required_time = 15
        # elif fl >= 100 and fh <= 400:
        #     required_time = 6
        # elif fl >= 500 and fh <= 5000:
        #     required_time = 4

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
            if time_entry != int(time_entry):  # Tipo float introducido -> cambio a int
                self.delete_and_change_entry_value(self.time_entry, int(time_entry))
                messagebox.showwarning(
                    "ADVERTENCIA",
                    f"Se ha cambiado automaticamente la duración a {self.time_entry.get()} segundos por haber introducido un valor decimal",
                )
                
    def check_selected_time_type(self):
        """Comprobar el tipo de los segundos elegidos"""
        try:
            float(self.time_entry.get())  # Obtengo el valor de tiempo introducido e intento convertirlo a float
        except:
            match self.time_entry.get():
                case "":
                    messagebox.showinfo(
                        "INFORMACIÓN",
                        f"Como no se ha introducido ninguna duración se establece por defecto {DURATION} segundos",
                    )
                    self.delete_and_change_entry_value(self.time_entry, DURATION)
                case _:
                    messagebox.showerror(
                        "ERROR",
                        f"La duración introducida no sigue ningún fomrato válido, introduzca un número o deje en blanco para valor por defecto ({DURATION})",
                    )
        else:   
            self.check_medition_time_iso_16283_1()

    def clear_bands(self):
        """Vacía los valores de las bandas de frecuencias al cambiar de tipo de banda"""
        self.combo_low_freq.set("")
        self.combo_high_freq.set("")

    def change_band_type(self):
        """Modifica dinámicamente las bandas seleccionables según el tipo de filtro elegido"""
        if self.band_type.get() == "1/3":
            bands = NOMINAL_THIRDOCTAVE_FREC

        elif self.band_type.get() == "1/1":
            bands = NOMINAL_OCTAVE_FREC

        return bands

    def update_bandpass(self, bands, fl, fh):
        """Actualzia las bandas seleccionables si se marca el filtro paso banda"""
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

    def update_bands(self):
        """Actualiza las bandas a seleccionar en los desplegables de la interfaz"""
        bands = self.change_band_type()

        # Frecuencias de corte marcadas
        fl = self.combo_low_freq.get()
        fh = self.combo_high_freq.get()

        # Ver el tipo de filtro seleccionado
        filter_type = self.filter_type.get()

        if filter_type != "":
            # Se activan los desplegables para selccionar bandas
            self.combo_low_freq.state(["!disabled"])
            self.combo_high_freq.state(["!disabled"])

            if filter_type == "low_pass":
                self.combo_low_freq.set(bands[0])
                self.combo_low_freq.state(["disabled"])
                self.combo_high_freq["values"] = bands

            elif filter_type == "high_pass":
                self.combo_high_freq.set(bands[-1])
                self.combo_high_freq.state(["disabled"])
                self.combo_low_freq["values"] = bands

            elif filter_type == "band_pass":
                self.update_bandpass(bands, fl, fh)

            elif filter_type == "notch":
                # FALTA DESARROLLAR EL FILTRO NOTCH
                self.update_bandpass(bands, fl, fh)

            elif filter_type == "all_pass":
                # FALTA DESARROLLAR EL FILTRO
                self.combo_low_freq.set(bands[0])
                self.combo_low_freq.state(["disabled"])
                self.combo_high_freq.set(bands[-1])
                self.combo_high_freq.state(["disabled"])

    def apply_filter(self):
        """Realiza el filtrado seleccinado"""
        self.stop_noise()  # Verificar si el hilo de reproducción está activo y si lo está lo apaga

        # Obtiene la duración introducida para el audio (por defecto duración en config.py)
        print(self.time_entry.get())
        time_entry = int(self.time_entry.get())

        # Obtener valores de la variable actual del ruido y del tipo de filtro
        selected_noise = self.noise_type.get()
        selected_filter = self.band_type.get()
        bandas_a_filtrar = [
            float(self.combo_low_freq.get()),
            float(self.combo_high_freq.get()),
        ]
        print("APLICO FILTRO")
        # Decidir tipo de filtro y de ruido para filtrar
        if (
            selected_noise != ""
            and selected_filter != ""
            and bandas_a_filtrar != ""
        ):

            if selected_noise == "WHITE NOISE":  # RUIDO BLANCO
                noise_data = generate_white_noise(time_entry, SAMPLE_RATE)

            elif selected_noise == "PINK NOISE":  # RUIDO ROSA
                noise_data = generate_pink_noise(time_entry, SAMPLE_RATE)

            if selected_filter == "1/1":  # 1/1 OCTAVA
                (
                    self.filtered_noise,
                    self.band_levels,
                    self.fm,
                    self.fl_selected_bands,
                    self.fh_selected_bands,
                ) = octaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

            elif selected_filter == "1/3":  # 1/3 OCTAVA
                (
                    self.filtered_noise,
                    self.band_levels,
                    self.fm,
                    self.fl_selected_bands,
                    self.fh_selected_bands,
                ) = thirdOctaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

            self.create_plot()

        # Muestra ventana de error si no hay ruido y/o filtro seleccionado
        else:
            messagebox.showerror(
                "Advertencia",
                "Debe seleccionar un tipo de filtro, de ruido y bandas a filtrar",
            )

    def start_noise_thread(self):
        """Inicia el hilo para reproducir el ruido"""
        self.stop_noise()  # Verificar si el hilo de reproducción está activo y si lo está lo apaga

        self.control_noise_event.clear()  # Limpia el evento de detención

        self.noise_thread = threading.Thread(
            target=self.play_noise,  # Función que reproduce el ruido
            daemon=True,  # Hilo se detendrá si la ventana principal se cierra
        )  # Hilo para reproducir el ruido filtrado

        self.noise_thread.start()  # Iniciar el nuevo hilo

    def stop_noise(self):
        """Detiene el ruido generado"""
        # Si el hilo está activo y en ejecución, se detiene
        if self.noise_thread and self.noise_thread.is_alive():
            self.control_noise_event.set()  # Establecer evento de detención en activo
            self.noise_thread.join()  # Esperar a que el hilo termine
            self.noise_thread = None  # Reiniciar el hilo

    def play_noise(self):
        """Reproduce el ruido generado"""
        p = pyaudio.PyAudio()  # Inicializar PyAudio

        stream = p.open(
            format=pyaudio.paInt16,  # Formato de audio
            channels=1,  # 1 = Mono
            rate=SAMPLE_RATE,  # Frecuencia de muestreo
            output=True,  # Salida de audio
        )  # Abrir stream de audio

        chunk = 1024  # Tamaño del chunk
        start = 0  # Inicio de la reproducción

        while not self.control_noise_event.is_set() and start < len(
            self.filtered_noise
        ):  # Mientras el evento no esté activado
            end = start + chunk  # Fin de la reproducción
            stream.write(
                self.filtered_noise[start:end].astype(np.int16).tobytes()
            )  # Reproducir audio
            start = end  # Actualizar inicio de la reproducción

        stream.stop_stream()  # Detener stream
        stream.close()  # Cerrar stream
        p.terminate()  # Cerrar PyAudio

    def create_plot(self):
        """Crea y actualiza la gráfica de la interfaz"""
        # Decidir qué frecuencias nominales utilizar
        if len(self.fm) == len(NOMINAL_THIRDOCTAVE_FREC):
            nominal_freq = NOMINAL_THIRDOCTAVE_FREC

        elif len(self.fm) == len(NOMINAL_OCTAVE_FREC):
            nominal_freq = NOMINAL_OCTAVE_FREC

        # Crear una figura de Matplotlib
        self.figure = Figure(figsize=(7, 5))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Niveles por bandas")

        # Graficar niveles por bandas con barras uniformes
        widths = np.array(self.fh_selected_bands) - np.array(
            self.fl_selected_bands
        )  # Calcular ancho de las barras en escala logarítmica
        self.ax.bar(
            self.fl_selected_bands,
            self.band_levels,
            width=widths,
            align="edge",
            color="skyblue",
            edgecolor="black",
        )
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frecuencia (Hz)")
        self.ax.set_ylabel("Nivel (dB)")

        # Personalizar el eje X para mostrar todas las frecuencias centrales
        self.ax.set_xticks(self.fm)
        self.ax.set_xticklabels(
            [
                f"{int(freq)} Hz" if freq >= 100 else f"{freq:.1f} Hz"
                for freq in nominal_freq
            ],
            rotation=45,
        )

        # Agregar la cuadrícula
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        self.figure.tight_layout()

        # Personalizar la barra de estado para mostrar x e y en escala logarítmica
        self.ax.format_coord = (
            lambda x, y: f"x = {x:.1f} Hz, y = {y:.1f} dB"
        )  # Formato para mostrar Hz y dB

        # Crear un lienzo de Tkinter para la figura de Matplotlib
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=0, column=1, padx=10, pady=10
        )  # Mostrar el lienzo en la ventana

    def init_widget_types(self):
        """Inicializa como variables de clase los diferentes widgets"""
        self.noise_type = tk.StringVar()
        self.band_type = tk.StringVar()
        self.filter_type = tk.StringVar()
        self.radio_btn_lowpass = ttk.Radiobutton()
        self.radio_btn_highpass = ttk.Radiobutton()
        self.radio_btn_bandpass = ttk.Radiobutton()
        self.radio_btn_notch = ttk.Radiobutton()
        self.radio_btn_allpass = ttk.Radiobutton()
        self.combo_low_freq = ttk.Combobox()
        self.combo_high_freq = ttk.Combobox()
        self.time_entry = ttk.Entry()
        self.btn_apply_filter = ttk.Button()
        self.btn_stop = ttk.Button()

    def on_filter_type_selected(self):
        """Aplica todo cuando se selecciona un radio button de tipo de filtro"""
        self.btn_apply_filter.state(["disabled"])
        self.clear_bands()
        self.update_bands()
        self.check_conditions()

    def on_band_type_selected(self):
        """Aplica todo cuando se selecciona un radio button de tipo de banda"""
        self.btn_apply_filter.state(["disabled"])

        self.radio_btn_lowpass.state(["!disabled"])
        self.radio_btn_highpass.state(["!disabled"])
        self.radio_btn_bandpass.state(["!disabled"])
        self.radio_btn_notch.state(["!disabled"])
        self.radio_btn_allpass.state(["!disabled"])

        self.clear_bands()
        self.update_bands()
        self.check_conditions()

    def create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Marco para agrupar los widgets
        self.frm_options = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_options.grid(padx=10, pady=10, row=0, column=0, sticky="n")

        # Marco para el gráfico
        self.frm_graphic = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_graphic.grid(padx=10, pady=10, row=0, column=1, sticky="n")

        # >>>>> Selección de ruido <<<<<
        ttk.Label(self.frm_options, text="Seleccione el tipo de ruido:").grid(
            row=0, sticky="w"
        )
        radio_btn_pink = ttk.Radiobutton(
            self.frm_options,
            text="Ruido rosa",
            variable=self.noise_type,
            value="PINK NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido rosa
        radio_btn_pink.grid(row=1, sticky="w")

        radio_btn_white = ttk.Radiobutton(
            self.frm_options,
            text="Ruido blanco",
            variable=self.noise_type,
            value="WHITE NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido blanco
        radio_btn_white.grid(row=2, sticky="w")

        # >>>>> Selección de tipo de filtro <<<<<
        ttk.Label(
            self.frm_options,
            text="\nSeleccione el tipo de banda de frecuencia:",
        ).grid(row=3, sticky="w")

        radio_btn_octave = ttk.Radiobutton(
            self.frm_options,
            text="Octavas",
            variable=self.band_type,
            value="1/1",
            command=self.on_band_type_selected,
        )  # Crear botón para octavas
        radio_btn_octave.grid(row=4, sticky="w")

        radio_btn_third_octave = ttk.Radiobutton(
            self.frm_options,
            text="Tercios de octavas",
            variable=self.band_type,
            value="1/3",
            command=self.on_band_type_selected,
        )  # Crear botón para tercios de octavas
        radio_btn_third_octave.grid(row=5, sticky="w")

        # >>>>> Selección de tipo de filtro <<<<<
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

        # >>>>> Selección de las bandas <<<<<
        ttk.Label(
            self.frm_options, text="\nSeleccione las bandas a filtrar:"
        ).grid(row=12, sticky="w")

        ttk.Label(self.frm_options, text="Banda inferior").grid(
            row=13, column=0
        )
        ttk.Label(self.frm_options, text="Banda superior").grid(
            row=13, column=1
        )

        self.combo_low_freq = ttk.Combobox(
            self.frm_options, state="readonly", postcommand=self.update_bands
        )
        self.combo_low_freq.grid(row=14, column=0, sticky="w")
        self.combo_low_freq.state(["disabled"])
        self.combo_low_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        self.combo_high_freq = ttk.Combobox(
            self.frm_options, state="readonly", postcommand=self.update_bands
        )
        self.combo_high_freq.grid(row=14, column=1, sticky="w")
        self.combo_high_freq.state(["disabled"])
        self.combo_high_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        # >>>>> Selección del tiempo de ruido <<<<<
        ttk.Label(
            self.frm_options, text="\nIntroduzca los segundos a reproducir:"
        ).grid(row=15, sticky="w")
        self.time_entry = ttk.Entry(self.frm_options)
        self.time_entry.grid(row=16)

        ttk.Label(self.frm_options, text="\n").grid(
            row=17
        )  # Espacio en blanco antes de los botones

        # >>>>> Realizar el filtro <<<<<
        self.btn_apply_filter = ttk.Button(
            self.frm_options,
            text="APLICAR EL FILTRO",
            command=lambda: [
                self.check_selected_time_type(),
                self.apply_filter(),
                self.check_conditions(),
            ],
            state="disabled",
        )
        self.btn_apply_filter.grid(row=18, columnspan=2)

        # >>>>> Botón de reproducción <<<<<
        btn_play_noise = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: self.start_noise_thread(),
        )
        btn_play_noise.grid(row=19, columnspan=2)

        # >>>>> Botón STOP <<<<<
        self.btn_stop = ttk.Button(
            self.frm_options,
            text="STOP REPRODUCCIÓN",
            command=lambda: self.control_noise_event.set(),
            state="!disbaled",
        )
        self.btn_stop.grid(row=20, columnspan=2)
