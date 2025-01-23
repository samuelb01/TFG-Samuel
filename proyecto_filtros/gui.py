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

# Realiza el filtrado
def apply_filter():

    # Obtener valores de la variable actual del ruido y del tipo de filtro
    selected_noise = noise_type.get()
    print(selected_noise)
    selected_filter = filter_type.get()
    # bandas_a_filtrar = [int(combo_low_freq.get()), int(combo_high_freq.get())]
    
    # Decidir tipo de filtro y de ruido para filtrar
    if selected_noise != "" and selected_filter != "" and bandas_a_filtrar != "":

        if selected_noise == "WHITE NOISE": # RUIDO BLANCO
            noise_data = generate_white_noise(DURATION, SAMPLE_RATE)

        elif selected_noise == "PINK NOISE":    #RUIDO ROSA
            noise_data = generate_pink_noise(DURATION, SAMPLE_RATE)
            

        if selected_filter == "1/1":    # 1/1 OCTAVA
            octaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

        elif selected_filter == "1/3":  # 1/3 OCTAVA
            thirdOctaveFilter(noise_data, SAMPLE_RATE, bandas_a_filtrar)

    # Muestra ventana de error si no hay ruido y/o filtro seleccionado
    else:
        messagebox.showerror("Advertencia", "Debe seleccionar un tipo de filtro y de ruido")


def change_bands():
    """
    Modifica dinámicamente las bandas seleccionables según el tipo de filtro elegido.

    Returns:
        list: Señal de ruido rosa.
    """
    selected_filter = filter_type.get()
    try:
        fl = combo_low_freq.get()
    except:
        fl = None

    if selected_filter == "1/3":
        bands = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400,
                    500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000,
                    6300, 8000, 10000, 12500, 16000, 20000]
        
    elif selected_filter == "1/1":
        bands = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

    return bands


def update_bands():
    bands = change_bands()
    combo_low_freq["values"] = bands
    combo_high_freq["values"] = bands


# Configuración principal de la ventana
root = tk.Tk()  # Ventana principal de la interfaz
root.title("Ecualizador Gráfico")  # Título de la ventana
root.geometry("900x500")  # Tamaño de la ventana

# Variable para el tipo de ruido elegido
noise_type = tk.StringVar()
filter_type = tk.StringVar()
filter_type.set("1/1")

# Marco para agrupar los widgets
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
radio_btn_octave = ttk.Radiobutton(frm_options, text="Octavas", variable=filter_type, value="1/1", command=update_bands)    # Crear botón para ruido rosa
radio_btn_octave.grid()
radio_btn_third_octave = ttk.Radiobutton(frm_options, text="Tercios de octavas", variable=filter_type, value="1/3", command=update_bands)    # Crear botón para ruido blanco
radio_btn_third_octave.grid()


# Selección de las bandas
ttk.Label(frm_options, text="Seleccione las bandas a filtrar").grid()
combo_low_freq = ttk.Combobox(
    state="readonly",
    values=change_bands()
)
combo_low_freq.grid()
combo_low_freq.bind("<<ComboboxSelected>>", update_bands)

combo_high_freq = ttk.Combobox(
    state="readonly",
    values=change_bands()
)
combo_high_freq.grid()
combo_low_freq.bind("<<ComboboxSelected>>", update_bands)


# Realizar el filtro
btn_01 = ttk.Button(frm_options, text="APLICAR EL FILTRO", command=lambda: apply_filter())
btn_01.grid()



# Bucle principal de la aplicación
root.mainloop()