# Herramienta de Generación, Filtrado y Ecualización de Ruido para Acústica Edificatoria

Este proyecto es una aplicación avanzada desarrollada en Python para la generación y procesamiento de señales de ruido orientada a la medición del aislamiento acústico en edificación. Ha sido diseñada como parte de un **Trabajo de Fin de Grado (TFG)**, integrando requisitos técnicos de normativas internacionales ISO.

## 1. Introducción
La aplicación permite generar señales de ruido blanco y rosa, aplicar filtrados precisos en bandas de octava y tercio de octava, y realizar una ecualización personalizada. El objetivo principal es proporcionar una herramienta que facilite el cumplimiento de las normas de medición acústica, asegurando que la señal emitida por la fuente cumpla con los espectros y niveles de presión exigidos.

## 2. Instalación y Requisitos

### 2.1 Requisitos del Sistema
*   **Python 3.10** o superior.
*   **Bibliotecas necesarias:** Las dependencias se encuentran detalladas en el archivo `requirements.txt`:
    *   `numpy`: Procesamiento numérico y manejo de arrays de audio.
    *   `scipy`: Diseño de filtros y procesamiento de señales.
    *   `matplotlib`: Generación de gráficas interactivas.
    *   `pyaudio`: Reproducción de audio en tiempo real.

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

### 2.3 Generación y Uso del Ejecutable
Si se desea utilizar la aplicación en sistemas sin Python instalado, se puede generar un ejecutable mediante **PyInstaller**:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile scripts/main.py
```
*(Nota: Asegúrese de incluir las dependencias y recursos necesarios si se añaden archivos externos en el futuro).*

## 3. Manual de Usuario Detallado

### 3.1 Configuración de la Señal (Pestaña Main)
La pestaña principal permite configurar la señal de referencia inicial.

`[IMAGEN: Marcador de posición para Captura de Pantalla - Interfaz Principal]`

1.  **Tipo de Ruido:** Seleccione entre **Ruido Rosa** (común para aislamiento aéreo) o **Ruido Blanco**.
2.  **Tipo de Banda:** Escoja entre bandas de **Octava** o **Tercios de Octava**.
3.  **Configuración del Filtro:** Seleccione el tipo de filtro (Paso Bajo, Paso Alto, Paso Banda o Paso Todo) y defina las frecuencias de corte deseadas.
4.  **Duración:** Introduzca la duración en segundos. La aplicación validará automáticamente este tiempo según la frecuencia de corte inferior para cumplir con la norma **ISO 16283-1**.
5.  **Procesamiento:** Pulse **APLICAR EL FILTRO**. La aplicación procesará la señal y mostrará el espectro resultante en la gráfica derecha.
6.  **Reproducción:** Utilice los botones **REPRODUCIR** y **STOP REPRODUCCIÓN** para escuchar la señal generada.

### 3.2 Ecualización y Validación (Pestaña Equalizer)
Tras aplicar un filtro, se activa la pestaña de ecualización para ajustar la linealidad de la fuente.

`[IMAGEN: Marcador de posición para Captura de Pantalla - Pestaña Ecualizador]`

*   **Sliders de Ganancia:** Permiten ajustar cada banda de frecuencia individualmente en un rango de ±10 dB.
*   **Introducción de Datos:**
    *   **Manual:** Introduzca los niveles medidos en el recinto fuente para cada banda.
    *   **Archivo CSV:** Cargue datos promediados directamente desde un archivo CSV.
*   **Validación Automática:** La aplicación comprobará si la diferencia de nivel entre bandas adyacentes supera los **8 dB**. En caso de incumplimiento, los campos de entrada se marcarán en **rojo**.
*   **Actualización:** Al pulsar **Aplicar ecualización**, la señal de audio se recalcula y las gráficas se actualizan en tiempo real.

## 4. Normativa Implementada

### 4.1 ISO 61260-1:2014 - Filtros de Banda Octava y de Octava Fraccionaria
La aplicación utiliza filtros digitales Butterworth de orden superior (Orden 32) para garantizar una selectividad extrema. La herramienta incluye una función de verificación que compara la respuesta en frecuencia del filtro diseñado con los límites de aceptación de **Clase 1** definidos en la norma, asegurando la validez de los resultados para mediciones oficiales.

### 4.2 ISO 16283-1:2014 - Medición del Aislamiento Acústico en Edificios
Se han integrado controles automáticos basados en esta norma:
*   **Tiempo de promediado (Apartado 7.7):** Validación de la duración mínima según la frecuencia (ej. mínimo 15s para bandas inferiores a 80 Hz).
*   **Linealidad del espectro (Apartado 7.2):** Verificación del requisito de "diferencias no superiores a 8 dB entre bandas de tercio de octava adyacentes" en el recinto fuente.

## 5. Arquitectura del Código (Descripción Técnica)

El software ha sido desarrollado siguiendo principios de programación orientada a objetos (POO) para facilitar su mantenimiento y escalabilidad.

*   **`GUI` (scripts/gui/gui.py):** Clase principal que orquestra la interfaz gráfica. Gestiona los eventos de usuario, la validación de entradas y la comunicación entre los módulos de procesamiento y visualización.
*   **`Filter` (scripts/filter/filter.py):** Encapsula la lógica matemática del filtrado. Implementa el diseño de filtros en formato **SOS (Second-Order Sections)** para maximizar la estabilidad numérica en filtros de orden alto.
*   **`NoiseGenerator` (scripts/noise_generator/noise_generator.py):** Responsable de la síntesis de señales. Utiliza algoritmos de transformada de Fourier (FFT) para generar ruido rosa con una pendiente precisa de -3 dB/octava.
*   **`AudioPlayer` (scripts/audio_player/audio_player.py):** Gestiona la salida de audio mediante un hilo independiente (**threading**), lo que permite que la interfaz gráfica siga siendo funcional y fluida durante la reproducción.
*   **`FilterPlotter` (scripts/filter_plotter/filter_plotter.py):** Hereda de la lógica de filtrado para proporcionar representaciones visuales avanzadas mediante Matplotlib, incluyendo herramientas de inspección de datos al pasar el cursor (hover).
*   **`config.py`:** Archivo de configuración que centraliza parámetros críticos como frecuencias nominales, límites de la norma ISO y parámetros de hardware.

---
**Autor:** Samuel Bellón Elipe
**Grado en Ingeniería**
