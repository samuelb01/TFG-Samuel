# Autor: Samuel Bellón Elipe
# Constantes para los filtros
NOMINAL_THIRDOCTAVE_FREQ = [
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
NOMINAL_OCTAVE_FREQ = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
G = 10 ** (3 / 10)  # Octave frecuency ratio
FR = 1000  # Reference frequency
FILTER_ORDER = 32  # Orden del filtro
DURATION = 60 # Duración del ruido
SAMPLE_RATE = 48000 # Frecuencia de muestreo