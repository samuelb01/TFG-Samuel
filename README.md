# Herramienta de Generación, Filtrado y Ecualización de Ruido para Ensayos de Aislamiento Acústico

Este proyecto es una aplicación avanzada desarrollada en Python para la generación y procesamiento de señales de ruido orientada a la medición del aislamiento acústico. Ha sido diseñada como parte de un **Trabajo de Fin de Grado (TFG)**, integrando requisitos técnicos de normativas internacionales ISO.

## 1. Introducción
La aplicación permite generar señales de ruido blanco y rosa, aplicar filtrados precisos en bandas de octava y tercio de octava, y realizar una ecualización personalizada. El objetivo principal es proporcionar una herramienta que facilite la generación y preparación de señales utilizadas en ensayos de aislamiento acústico, permitiendo ajustar el espectro de la señal para cumplir los requisitos de uniformidad espectral establecidos en normas de medición acústica.

La aplicación permite:

- Generar ruido blanco o rosa.
- Filtrar la señal en bandas de octava o tercio de octava.
- Seleccionar el rango de bandas a utilizar.
- Visualizar el espectro en octavas o tercios de octava de la señal generada.
- Ajustar el nivel de cada banda mediante un ecualizador.
- Introducir datos medidos manualmente o desde un archivo CSV.
- Reproducir la señal generada desde la propia interfaz.
- Exportar la señal final a un archivo WAV.


## 2. Instalación y Requisitos

### 2.1 Requisitos del Sistema
*   **Python 3.10** o superior.
*   **Bibliotecas necesarias:** Las dependencias se encuentran detalladas en el archivo `requirements.txt`:
    *   `numpy`: Procesamiento numérico y manejo de arrays de audio.
    *   `scipy`: Diseño de filtros y procesamiento de señales.
    *   `matplotlib`: Generación de gráficas interactivas.
    *   `pyaudio`: Reproducción de audio en tiempo real.

Todas las dependencias se encuentran especificadas en: 
```
requirements.txt
```

### 2.2 Instalación desde el Código Fuente
1.  Clonar el repositorio o descargar los archivos del proyecto.
2.  (Recomendado) Crear un entorno virtual:
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    ```
3.  Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecutar la aplicación:
    ```bash
    python scripts/main.py
    ```

## 3. Manual de usuario

La interfaz se divide en dos secciones principales:

- **Configuración y generación de la señal**
- **Ecualización**


## 4. Generación y filtrado de ruido

La pestaña principal permite configurar la señal que se utilizará como referencia.

### 4.1 Selección del tipo de ruido

Se puede seleccionar entre:

- **Ruido blanco**
- **Ruido rosa**

El ruido rosa suele emplearse con mayor frecuencia en ensayos acústicos debido a su distribución energética por octava.

---

### 4.2 Selección del tipo de banda

La señal puede filtrarse utilizando:

- **Bandas de octava**
- **Bandas de tercio de octava**

---

### 4.3 Selección del tipo de filtro

Dependiendo de la configuración seleccionada, se puede aplicar:

- Filtro paso bajo
- Filtro paso alto
- Filtro paso banda
- Filtro paso todo

---

### 4.4 Selección del rango de frecuencias

El usuario debe seleccionar:

- frecuencia inferior
- frecuencia superior

Estas frecuencias definen las bandas que se utilizarán en el filtrado.

---

### 4.5 Duración de la señal

Se debe introducir la duración del ruido en segundos.

La aplicación incluye validaciones relacionadas con los tiempos mínimos recomendados en determinadas bandas según criterios de medición acústica.

---

### 4.6 Aplicar el filtrado

Pulsar **Apply Filter** para generar la señal.

La aplicación:

1. Genera la señal de ruido.
2. Aplica el filtrado seleccionado.
3. Calcula los niveles por banda.
4. Representa el espectro en la gráfica.

---

### 4.7 Reproducción de la señal

La señal generada puede reproducirse desde la interfaz mediante los botones:

- **Play Noise**
- **Stop**

La reproducción se ejecuta en un hilo independiente para no bloquear la interfaz gráfica.

---

### 4.8 Exportar señal a WAV

Una vez generada la señal filtrada se puede guardar como archivo WAV.

Los archivos se guardan automáticamente en la carpeta:

```
data/
```



## 5. Ecualización de la señal

Una vez generado el filtrado se habilita la pestaña **Equalizer**.

Esta sección permite modificar el nivel de cada banda de frecuencia para ajustar el espectro de la señal.


### 5.1 Ajuste mediante controles de ganancia

Cada banda dispone de un control deslizante (slider) que permite modificar su ganancia aproximadamente en un rango de:

```
±10 dB
```

Los cambios se aplican al pulsar **Apply Equalization**.


### 5.2 Introducción manual de datos

El usuario puede introducir manualmente niveles medidos en el recinto fuente.

Estos valores pueden utilizarse para comprobar la uniformidad espectral de la señal.


### 5.3 Importación de datos desde CSV

También es posible cargar niveles desde un archivo `.csv`.

Formato requerido:

```
31.5;40;50;63;80;100;125;160
67;89;-45;12.12;14.6;75.2;78.5;80.1
```

Primera fila → frecuencias nominales  
Segunda fila → niveles en dB



## 6. Generación de ruido desde línea de comandos

El proyecto también incluye un generador de ruido que puede ejecutarse desde terminal.

Ejemplo:

```bash
python noise_generator.py --type white --duration 10
```

Ejemplo con archivo de salida:

```bash
python noise_generator.py --type pink --duration 5 --output ruido.wav
```

Si no se especifica `--output`, el archivo se guardará automáticamente en:

```
data/
```


## 7. Normativa Implementada

El desarrollo del proyecto toma como referencia criterios de las siguientes normas:

### 7.1 ISO 61260-1:2014 - Filtros de Banda Octava y de Octava Fraccionaria
Filtros de banda de octava y fracciones de octava utilizados en análisis acústico.


### 7.2 ISO 16283-1:2014 - Medición del Aislamiento Acústico en Edificios
Medición del aislamiento acústico en edificios. Se han integrado controles automáticos basados en esta norma:
*   **Tiempo de promediado (Apartado 7.7):** Validación de la duración mínima según la frecuencia (ej. mínimo 15s para bandas inferiores a 80 Hz).
*   **Generación de campo acústico (Apartado 7.2):** Verificación del requisito de "diferencias no superiores a 8 dB entre bandas de tercio de octava adyacentes" en el recinto fuente.

## 8. Arquitectura del Código (Descripción Técnica)

El software ha sido desarrollado siguiendo principios de programación orientada a objetos (POO) para facilitar su mantenimiento y escalabilidad.

*   **`GUI` (scripts/gui/gui.py):** Clase principal que orquestra la interfaz gráfica. Gestiona los eventos de usuario, la validación de entradas y la comunicación entre los módulos de procesamiento y visualización.
*   **`Filter` (scripts/filter/filter.py):** Encapsula la lógica matemática del filtrado. Implementa el diseño de filtros en formato **SOS (Second-Order Sections)** para maximizar la estabilidad numérica en filtros de orden alto.
*   **`NoiseGenerator` (scripts/noise_generator/noise_generator.py):** Responsable de la síntesis de señales. Utiliza algoritmos de transformada de Fourier (FFT) para generar ruido rosa con una pendiente precisa de -3 dB/octava.
*   **`AudioPlayer` (scripts/audio_player/audio_player.py):** Gestiona la salida de audio mediante un hilo independiente (**threading**), lo que permite que la interfaz gráfica siga siendo funcional durante la reproducción.
*   **`FilterPlotter` (scripts/filter_plotter/filter_plotter.py):** Hereda de la lógica de filtrado para proporcionar representaciones visuales avanzadas mediante Matplotlib, incluyendo herramientas de inspección de datos al pasar el cursor.
*   **`config.py`:** Archivo de configuración que centraliza parámetros críticos como frecuencias nominales o parámetros y límites definidos por las normas ISO empleadas.

---
**Autor:** Samuel Bellón Elipe