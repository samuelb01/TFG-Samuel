import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import matplotlib.pyplot as plt

from filters3 import thirdOctaveFilter, octaveFilter  # Importar las funciones necesarias
from noise_generator import generate_white_noise, generate_pink_noise    # Importar funciones para crear ruidos

# Parámetros para generar ruidos
DURATION = 60   # Duración del audio a crear
SAMPLE_RATE = 48000 # Frecuencia de muestreo

# Nombre de los archivos de ruido
PINK_NOISE = "pink_noise_mono_48khz_16bits.wav"
# WHITE_NOISE = generate_white_noise(DURATION, SAMPLE_RATE)

def apply_filter():
    # Obtener valores de la variable actual del ruido y del tipo de filtro
    selected_noise = noise_type.get()
    selected_filter = filter_type.get()

    if selected_noise != "" and selected_filter != "":

        if selected_noise == "WHITE NOISE":
            noise_data = generate_white_noise(DURATION, SAMPLE_RATE)

        elif selected_noise == "PINK NOISE":
            noise_data = generate_pink_noise(DURATION, SAMPLE_RATE)
            

        if selected_filter == "1/1":
            octaveFilter(noise_data, SAMPLE_RATE)

        elif selected_filter == "1/3":
            thirdOctaveFilter(noise_data, SAMPLE_RATE)

    else:
        messagebox.showerror("Advertencia", "Debe seleccionar un tipo de filtro y de ruido")


# Configuración principal de la ventana
root = tk.Tk()  # Ventana principal de la interfaz
root.title("Ecualizador Gráfico")   # Título de la ventana
root.geometry("900x500")

# Variable para el tipo de ruido elegido
noise_type = tk.StringVar()
filter_type = tk.StringVar()

frm_options = ttk.Frame(root, padding=10)
frm_options.grid(padx=10, pady=10)

# Selección de ruido
ttk.Label(frm_options, text="Seleccione el tipo de ruido").grid()
radio_btn_pink = ttk.Radiobutton(frm_options, text="Ruido rosa", variable=noise_type, value="PINK NOISE")    # Crear botón para ruido rosa
radio_btn_pink.grid()
radio_btn_white = ttk.Radiobutton(frm_options, text="Ruido blanco", variable=noise_type, value="WHITE NOISE")    # Crear botón para ruido blanco
radio_btn_white.grid()

# Selección de tipo de filtro
ttk.Label(frm_options, text="Seleccione el tipo de filtro").grid()
radio_btn_pink = ttk.Radiobutton(frm_options, text="Octavas", variable=filter_type, value="1/1")    # Crear botón para ruido rosa
radio_btn_pink.grid()
radio_btn_white = ttk.Radiobutton(frm_options, text="Tercios de octavas", variable=filter_type, value="1/3")    # Crear botón para ruido blanco
radio_btn_white.grid()

# Realizar el filtro
btn_01 = ttk.Button(frm_options, text="APLICAR EL FILTRO", command=lambda: apply_filter())
btn_01.grid()

# Bucle principal de la aplicación
root.mainloop()