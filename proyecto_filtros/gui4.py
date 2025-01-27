import tkinter as tk
from tkinter import ttk, messagebox

import pyaudio
import threading

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from filters4 import (
    thirdOctaveFilter,
    octaveFilter,
)  # Importar las funciones necesarias
from noise_generator import (
    generate_white_noise,
    generate_pink_noise,
)  # Importar funciones para crear ruidos

# Parámetros para generar ruidos
DURATION = 15  # Duración del audio a crear
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

        # Variables de control
        self.noise_type = tk.StringVar()
        self.filter_type = tk.StringVar()
        self.combo_low_freq = ttk.Combobox()
        self.combo_high_freq = ttk.Combobox()
        self.btn_apply_filter = ttk.Button()
        self.btn_stop = ttk.Button()

        # Variables de control (hilos de ejecución)
        self.noise_thread = None
        self.control_noise_event = threading.Event()

        # Variables una vez filtrado
        self.filtered_noise = None
        self.band_levels = None
        self.fm = None
        self.fl_selected_bands = None
        self.fh_selected_bands = None

        # Marco para agrupar los widgets
        self.frm_options = ttk.Frame(self.root, padding=10)
        self.frm_options.grid(padx=10, pady=10)

        # self.create_plot()

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
            self.btn_apply_filter.state(["!disabled"])

    # Vaciar los valores de las bandas de frecuencias si se cambia de filtro
    def clear_bands(self):
        self.combo_low_freq.set("")
        self.combo_high_freq.set("")

    def change_bands(self):
        """
        Modifica dinámicamente las bandas seleccionables según el tipo de filtro elegido.

        Returns:
            list: Señal de ruido rosa.
        """

        if self.filter_type.get() == "1/3":
            bands = NOMINAL_THIRDOCTAVE_FREC

        elif self.filter_type.get() == "1/1":
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

        self.stop_noise()  # Verificar si el hilo de reproducción está activo y si lo está lo apaga

        # Obtener valores de la variable actual del ruido y del tipo de filtro
        selected_noise = self.noise_type.get()
        selected_filter = self.filter_type.get()
        bandas_a_filtrar = [
            float(self.combo_low_freq.get()),
            float(self.combo_high_freq.get()),
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
                self.filtered_noise, self.band_levels, self.fm, self.fl_selected_bands, self.fh_selected_bands = octaveFilter(
                    noise_data, SAMPLE_RATE, bandas_a_filtrar
                )

            elif selected_filter == "1/3":  # 1/3 OCTAVA
                self.filtered_noise, self.band_levels, self.fm, self.fl_selected_bands, self.fh_selected_bands = thirdOctaveFilter(
                    noise_data, SAMPLE_RATE, bandas_a_filtrar
                )

            self.create_plot()

        # Muestra ventana de error si no hay ruido y/o filtro seleccionado
        else:
            messagebox.showerror(
                "Advertencia",
                "Debe seleccionar un tipo de filtro, de ruido y bandas a filtrar",
            )

    def start_noise_thread(self):  # Iniciar hilo para reproducir el ruido
        self.stop_noise()  # Verificar si el hilo de reproducción está activo y si lo está lo apaga

        self.control_noise_event.clear()  # Limpia el evento de detención

        self.noise_thread = threading.Thread(
            target=self.play_noise,  # Función que reproduce el ruido
            daemon=True,  # Hilo se detendrá si la ventana principal se cierra
        )  # Hilo para reproducir el ruido filtrado

        self.noise_thread.start()  # Iniciar el nuevo hilo

    def stop_noise(self):
        # Si el hilo está activo y en ejecución, se detiene
        if self.noise_thread and self.noise_thread.is_alive():
            self.control_noise_event.set() # Establecer evento de detención en activo
            self.noise_thread.join() # Esperar a que el hilo termine
            self.noise_thread = None # Reiniciar el hilo

    def play_noise(self):  # Reproducir el ruido filtrado

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
        # Decidir qué frecuencias nominales utilizar
        if len(self.fm) == len(NOMINAL_THIRDOCTAVE_FREC):
            nominal_freq = NOMINAL_THIRDOCTAVE_FREC

        elif len(self.fm) == len(NOMINAL_OCTAVE_FREC):
            nominal_freq = NOMINAL_OCTAVE_FREC

        # Crear una figura de Matplotlib sin especificar dpi
        self.figure = Figure(figsize=(7, 5)) 
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Niveles por bandas")

        # Graficar niveles por bandas con barras uniformes
        widths = np.array(self.fh_selected_bands) - np.array(self.fl_selected_bands) # Calcular ancho de las barras en escala logarítmica
        self.ax.bar(self.fl_selected_bands, self.band_levels, width=widths, align='edge', color='skyblue', edgecolor='black')
        self.ax.set_xscale('log')
        self.ax.set_xlabel('Frecuencia (Hz)')
        self.ax.set_ylabel('Nivel (dB)')


        # Personalizar el eje X para mostrar todas las frecuencias centrales
        self.ax.set_xticks(self.fm)
        self.ax.set_xticklabels([f"{int(freq)} Hz" if freq >= 100 else f"{freq:.1f} Hz" for freq in nominal_freq], rotation=45)

        # Agregar la cuadrícula
        self.ax.grid(True, which="both", linestyle='--', linewidth=0.5)
        self.figure.tight_layout()

        # Personalizar la barra de estado para mostrar x e y en escala logarítmica
        self.ax.format_coord = lambda x, y: f"x = {x:.1f} Hz, y = {y:.1f} dB"  # Formato para mostrar Hz y dB

        # Crear un lienzo de Tkinter para la figura de Matplotlib
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root) 
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10) # Mostrar el lienzo en la ventana

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
                self.clear_bands(),
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
                self.clear_bands(),
                self.change_bands(),
                self.combo_low_freq.state(["!disabled"]),
                self.combo_high_freq.state(["!disabled"]),
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
        self.btn_apply_filter = ttk.Button(
            self.frm_options,
            text="APLICAR EL FILTRO",
            command=lambda: [
                self.apply_filter(),
                self.check_conditions(),
            ],
            state="disabled",
        )
        self.btn_apply_filter.grid()

        # Botón de reproducción
        btn_play_noise = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: self.start_noise_thread(),
        )
        btn_play_noise.grid()

        # Botón STOP
        self.btn_stop = ttk.Button(
            self.frm_options,
            text="STOP REPRODUCCIÓN",
            command=lambda: self.control_noise_event.set(),
            state="!disbaled",
        )
        self.btn_stop.grid()


app = App()
app.create_widgets()
app.root.mainloop()
