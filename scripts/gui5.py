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

# Importar funciones para filtrar
from filters4 import (
    thirdOctaveFilter,
    octaveFilter,
)  

# Importar funciones para crear ruidos
from noise_generator import (
    generate_white_noise,
    generate_pink_noise
)

class App:
    def __init__(self):
        # Configuración principal de la ventana
        self.root = tk.Tk()  # Ventana principal de la interfaz
        self.root.title("Ecualizador Gráfico")

        # 85% del ancho de la pantalla para el gráfico y el 15% para el menú de opciones
        self.root.grid_columnconfigure(0, weight=15)
        self.root.grid_columnconfigure(1, weight=100)

        # 70% de la altura de la pantalla para el gráfico y el 30% para el menú de opciones
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=50)

        # Obtener tamaño de la pantalla en píxeles
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()

        # Tamaño de la ventana (+0+0 para que se situe en la esquina superior izquierda)
        # self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.state("zoomed")  # Pantalla completa
        
        # Variables de control (hilos de ejecución)
        self.noise_thread = None
        self.control_noise_event = threading.Event()

        # Variables una vez filtrado
        self.fm = None
        self.fl_selected_bands = None
        self.fm_selected_bands = None   
        self.fh_selected_bands = None
        self.filtered_noise = None
        self.band_levels = None
        self.bars = None
        self.label_var = None
        self.equalizer_scales = []  # Array con todos los deslizadores
        # Array con etiquetas de valores de los deslizadores
        self.equalizer_scales_labels = []  

        # crea las variables de control de la interfaz
        self.init_widget_types()

        # Crea la interfaz de la app y la inicializa
        self.create_widgets()
        self.root.mainloop()

    def apply_filter(self):
        """Realiza el filtrado seleccinado"""
        self.stop_noise()  # Verificar si el hilo de reproducción está activo y si lo está lo apaga

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
            # Muestra ventana de error si no hay ruido y/o filtro seleccionado
            messagebox.showerror(
                "Advertencia",
                "No se ha podido realizar el filtrado de la señal de referencia, revise el tipo de filtro, de ruido, bandas a filtrar y duración",
            )
        else:
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
                        self.fm_selected_bands,
                        self.fh_selected_bands,
                    ) = octaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

                elif selected_filter == "1/3":  # 1/3 OCTAVA
                    (
                        self.filtered_noise,
                        self.band_levels,
                        self.fm,
                        self.fl_selected_bands,
                        self.fm_selected_bands,
                        self.fh_selected_bands,
                    ) = thirdOctaveFilter(
                        noise_data, SAMPLE_RATE, bandas_a_filtrar
                    )

                self.create_plot()
                self.create_equalizer_gui()
                self.create_equalizer_gui_buttons()
    
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

        try:
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

        finally:
            stream.stop_stream()  # Detener stream
            stream.close()  # Cerrar stream
            p.terminate()  # Cerrar PyAudio

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
            self.btn_apply_filter.config(state="!disabled")
    
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

    def delete_and_change_entry_value(
        self, entry, value, initial_pos=0, final_pos=tk.END
    ):
        entry.delete(initial_pos, final_pos)
        entry.insert(initial_pos, value)

    def on_hover(self, event):
        """Función para mostrar el valor al pasar el cursor"""
        if (
            event.inaxes == self.ax
        ):  # Verifica si el cursor está dentro del área de la gráfica
            for bar, level, freq in zip(
                self.bars, self.band_levels, self.fm_selected_bands
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
                    self.plot_canvas.draw_idle()  # Redibuja solo si hay cambios
                    return
        self.annotation.set_visible(
            False
        )  # Oculta la anotación si no está sobre una barra
        self.plot_canvas.draw_idle()

    def create_plot(self):
        """Crea y actualiza la gráfica de la interfaz"""
        # Decidir qué frecuencias nominales utilizar
        if len(self.fm) == len(NOMINAL_THIRDOCTAVE_FREC):
            nominal_freq = NOMINAL_THIRDOCTAVE_FREC

        elif len(self.fm) == len(NOMINAL_OCTAVE_FREC):
            nominal_freq = NOMINAL_OCTAVE_FREC

        # Crear una figura de Matplotlib
        self.figure = Figure(figsize=(10, 5))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Niveles por bandas")

        # Graficar niveles por bandas con barras uniformes
        widths = np.array(self.fh_selected_bands) - np.array(
            self.fl_selected_bands
        )  # Calcular ancho de las barras en escala logarítmica
        self.bars = self.ax.bar(
            self.fl_selected_bands,
            self.band_levels,
            width=widths,
            align="edge",
            color="skyblue",
            edgecolor="black",
        )

        # Crear puntos en la misma posición que las barras, cambiarán con la ecualización
        self.scatter_points = self.ax.scatter(
            self.fm_selected_bands, self.band_levels, color="red", zorder=3
        )

        # Obtener el nivel máximo de las bandas y agregar 15 dB
        y_max = max(self.band_levels) + 15
        # Ajustar límites del eje Y
        self.ax.set_ylim(0, y_max)

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

        # Crear el "annotation" para mostrar el nivel en dB
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

        # Personalizar la barra de estado para mostrar x e y en escala logarítmica
        self.ax.format_coord = (
            lambda x, y: f"x = {x:.1f} Hz, y = {y:.1f} dB"
        )  # Formato para mostrar Hz y dB

        # Crear un lienzo de Tkinter para la figura de Matplotlib
        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(
            row=0, column=1, padx=10, pady=10
        )  # Mostrar el lienzo en la ventana

        # Conectar el evento de movimiento del ratón a la función
        self.plot_canvas.mpl_connect("motion_notify_event", self.on_hover)

    def update_plot_points(self):
        """Actualiza los puntos rojos en el gráfico según los valores de los sliders"""
        # Obtener los valores actuales de los sliders
        new_levels = [scale.get() for scale in self.equalizer_scales]

        # Sumar los valores de los sliders a los niveles originales
        print(self.equalizer_scales)
        equalized_levels = np.array(self.band_levels) + np.array(new_levels)

        # Actualizar la posición de los puntos en la gráfica
        # Generar matriz de coordenadas X (frecuencia) e Y (niveles ecualizazdos) para cada punto
        self.scatter_points.set_offsets(
            np.c_[self.fm_selected_bands, equalized_levels]
        )

        # Eliminar la línea anterior si existe
        if hasattr(self, "spline_line"):
            self.spline_line.remove()
        
        # Redibujar el gráfico con los nuevos valores
        self.plot_canvas.draw_idle()  # actualiza la gráfica sin bloquear la interfaz.

    def clear_frame(self, frame):
        """Elimina todos los widgets dentro del frame"""
        for widget in frame.winfo_children():
            widget.destroy()
            
    def clear_bands(self):
        """Vacía los valores de las bandas de frecuencias al cambiar de tipo de banda"""
        self.combo_low_freq.set("")
        self.combo_high_freq.set("")    

    def reset_scales(self):
        [scale.set(0) for scale in self.equalizer_scales]

    def change_band_type(self):
        """Modifica dinámicamente las bandas seleccionables según el tipo de filtro elegido"""
        if self.band_type.get() == "1/3":
            bands = NOMINAL_THIRDOCTAVE_FREC

        elif self.band_type.get() == "1/1":
            bands = NOMINAL_OCTAVE_FREC

        return bands
    
    def update_bandpass_type(self, bands, fl, fh):
        """Actualiza las bandas seleccionables si se marca el filtro paso banda"""
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
            self.combo_low_freq.config(state="readonly")
            self.combo_high_freq.config(state="readonly")

            if filter_type == "low_pass":
                self.combo_low_freq.set(bands[0])
                self.combo_low_freq.config(state="disabled")
                self.combo_high_freq["values"] = bands

            elif filter_type == "high_pass":
                self.combo_high_freq.set(bands[-1])
                self.combo_high_freq.config(state="disabled")
                self.combo_low_freq["values"] = bands

            elif filter_type == "band_pass":
                self.update_bandpass_type(bands, fl, fh)

            elif filter_type == "notch":
                # FALTA DESARROLLAR EL FILTRO NOTCH
                self.update_bandpass_type(bands, fl, fh)

            elif filter_type == "all_pass":
                # FALTA DESARROLLAR EL FILTRO
                self.combo_low_freq.set(bands[0])
                self.combo_low_freq.config(state="disabled")
                self.combo_high_freq.set(bands[-1])
                self.combo_high_freq.config(state="disabled")

    def update_plot_points(self):
        """Actualiza los puntos rojos en el gráfico según los valores de los sliders"""
        # Obtener los valores actuales de los sliders
        new_levels = [scale.get() for scale in self.equalizer_scales]

        # Sumar los valores de los sliders a los niveles originales
        equalized_levels = np.array(self.band_levels) + np.array(new_levels)

        # Actualizar la posición de los puntos en la gráfica
        # Generar matriz de coordenadas X (frecuencia) e Y (niveles ecualizazdos) para cada punto
        self.scatter_points.set_offsets(
            np.c_[self.fm_selected_bands, equalized_levels]
        )

        # Eliminar la línea anterior si existe
        if hasattr(self, "spline_line"):
            self.spline_line.remove()
        
        # Redibujar el gráfico con los nuevos valores
        self.plot_canvas.draw_idle()  # actualiza la gráfica sin bloquear la interfaz.
    
    def update_gain(self, value, label_var):
        """Actualiza la etiqueta del deslizador correspondiente y
        superpone en la gráfica la ganancia aplicada
        """
        label_var.set(f"{float(value):.1f} dB")
        self.update_plot_points()

    def activate_filter_buttons(self):
        """Activa los desplegables de la interfaz para las bandas"""
        self.combo_high_freq.config(state="readonly")
        self.combo_low_freq.config(state="readonly")

    def on_filter_type_selected(self):
        """Aplica todo cuando se selecciona un radio button de tipo de filtro"""
        self.btn_apply_filter.config(state="disabled")
        self.clear_bands()
        self.update_bands()
        self.check_conditions()
    
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

    def init_widget_types(self):
        """Inicializa como variables de clase los diferentes widgets"""
        self.noise_type = tk.StringVar()
        self.band_type = tk.StringVar()
        self.filter_type = tk.StringVar()

    def update_scales_values_and_labels(self, formatted_frequencies):
        for i, freq in enumerate(formatted_frequencies):
            label_var = tk.StringVar(value="0.0 dB")

            freq_label = ttk.Label(self.frm_scales, text=f"{freq} Hz")
            freq_label.grid(row=0, column=i)

            freq_scale = ttk.Scale(
                self.frm_scales,
                from_=10,
                to=-10,
                orient="vertical",
                command=lambda value, var=label_var: self.update_gain(
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

    def create_equalizer_gui(self):
        """Crea la interfaz con los botones delizables para ecualizazr la señal"""
        self.clear_frame(self.frm_equalizer)

        # Crear canvas con barra de desplazamiento para evitar desbordamiento en la pantalla
        self.scales_canvas = tk.Canvas(
            self.frm_equalizer, relief="groove", borderwidth=4
        )
        self.scales_scrollbar = tk.Scrollbar(
            self.frm_equalizer,
            orient="horizontal",
            command=self.scales_canvas.xview,
        )
        self.scales_canvas.config(
            xscrollcommand=self.scales_scrollbar.set
        )  # Sincronizar Canvas con la barra de desplazamiento

        # Se colocan el Canvas y la barra de desplazamiento
        self.scales_canvas.grid(row=0, column=0, sticky="nsew")
        self.scales_scrollbar.grid(row=1, column=0, sticky="ew")

        # Sliders ocupan todo el espacio del menú frm_equalizer
        self.frm_equalizer.grid_columnconfigure(0, weight=1)

        # Crear un Frame dentro del scales_canvas para colocar los sliders
        self.frm_scales = tk.Frame(self.scales_canvas)
        self.scales_canvas.create_window(
            (0, 0), window=self.frm_scales, anchor="nw"
        )

        band_type = self.band_type.get()
        self.equalizer_scales = []  # Reiniciar array con deslizadores
        self.equalizer_scales_labels = (
            []
        )  # Reiniciar etiquetas para evitar duplicados

        if band_type == "1/1":
            frequencies = np.array(
                [
                    NOMINAL_OCTAVE_FREC[
                        np.abs(NOMINAL_OCTAVE_FREC - f).argmin()
                    ]
                    for f in self.fm_selected_bands
                ]
            )
        elif band_type == "1/3":
            frequencies = np.array(
                [
                    NOMINAL_THIRDOCTAVE_FREC[
                        np.abs(NOMINAL_THIRDOCTAVE_FREC - f).argmin()
                    ]
                    for f in self.fm_selected_bands
                ]
            )

        # Formatear la salida para evitar ".0" en enteros
        formatted_frequencies = [
            int(f) if f.is_integer() else f for f in frequencies
        ]

        self.update_scales_values_and_labels(formatted_frequencies)

        # Actualizar el área desplazable (scrollable region)
        self.frm_scales.update_idletasks()  # Actualiza la interfaz antes de ajustar el área desplazable
        self.scales_canvas.config(
            scrollregion=self.scales_canvas.bbox("all")
        )  # Indica la región desplazable del Canvas, en este caso todo el Canvas
        self.scales_canvas.config(width=300, height=150)

    def create_equalizer_gui_buttons(self):
        """Crea los botones para gestionar las barras del ecualizador en el frm_equalizer_options"""
        btn_reset_scales = ttk.Button(
            self.frm_equalizer_options,
            text="REINICIAR DESLIZADORES",
            command=self.reset_scales,
        )
        btn_reset_scales.grid(row=0, column=0)

    def create_radio_buttons_noise_type(self):
        ttk.Label(self.frm_options, text="Seleccione el tipo de ruido:").grid(
            row=0, sticky="w"
        )
        self.radio_btn_pink = ttk.Radiobutton(
            self.frm_options,
            text="Ruido rosa",
            variable=self.noise_type,
            value="PINK NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido rosa
        self.radio_btn_pink.grid(row=1, sticky="w")

        self.radio_btn_white = ttk.Radiobutton(
            self.frm_options,
            text="Ruido blanco",
            variable=self.noise_type,
            value="WHITE NOISE",
            command=self.check_conditions,
        )  # Crear botón para ruido blanco
        self.radio_btn_white.grid(row=2, sticky="w")

    def create_radio_buttons_band_type(self):
        ttk.Label(
            self.frm_options,
            text="\nSeleccione el tipo de banda de frecuencia:",
        ).grid(row=3, sticky="w")

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
        self.combo_low_freq.config(state="disabled")
        self.combo_low_freq.bind("<<ComboboxSelected>>", self.check_conditions)

        self.combo_high_freq = ttk.Combobox(
            self.frm_options, state="readonly", postcommand=self.update_bands
        )
        self.combo_high_freq.grid(row=14, column=1, sticky="w")
        self.combo_high_freq.config(state="disabled")
        self.combo_high_freq.bind("<<ComboboxSelected>>", self.check_conditions)

    def create_entry_noise_time(self):
        ttk.Label(
            self.frm_options, text="\nIntroduzca los segundos a reproducir:"
        ).grid(row=15, sticky="w")
        self.time_entry = ttk.Entry(self.frm_options)
        self.time_entry.grid(row=16)

    def create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Marco para agrupar los widgets
        self.frm_options = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_options.grid(padx=10, pady=10, row=0, column=0, sticky="nsew")

        # Marco para el gráfico
        self.frm_graphic = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_graphic.grid(padx=10, pady=10, row=0, column=1, sticky="nsew")

        # Marco para el ecualizador
        self.frm_equalizer = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_equalizer.grid(
            padx=10, pady=10, row=1, column=1, sticky="nsew"
        )

        # Marco para las opciones del ecualizzador
        self.frm_equalizer_options = ttk.Frame(
            self.root, padding=10, relief="groove", borderwidth=2
        )
        self.frm_equalizer_options.grid(
            padx=10, pady=10, row=1, column=0, sticky="nsew"
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
                self.btn_play_noise.config(state="!disabled"),
            ],
            state="disabled",
        )
        self.btn_apply_filter.grid(row=18, columnspan=2)

        # >>>>> Botón de reproducción <<<<<
        self.btn_play_noise = ttk.Button(
            self.frm_options,
            text="REPRODUCIR",
            command=lambda: [
                self.start_noise_thread(),
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
                self.control_noise_event.set(),
                self.btn_stop.config(state="disabled"),
            ],
            state="disabled",
        )
        self.btn_stop.grid(row=20, columnspan=2)
