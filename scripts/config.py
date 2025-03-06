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
# Valor muy pequeño cercano a 0, usado en la norma ISO 61260-1 para obtener valores cercanos a las frecuencias del filtro paso-banda
EPSILON = 1e-10

# Límites de aceptación de la atenuación relativa para bandas de octava (clase 1)
ACCEPTANCE_LIMITS_CLASS1= {
    G**-4: [70, float("inf")],
    G**-3: [60, float("inf")],
    G**-2: [40.5, float("inf")],
    G**-1: [16.6, float("inf")],
    ((G**-0.5) - EPSILON): [1.2, float("inf")],
    ((G**-0.5) + EPSILON): [-0.4, 5.3],
    G**(-3/8): [-0.4, 1.4],
    G**(-1/4): [-0.4, 0.7],
    G**(-1/8): [-0.4, 0.5],
    1: [-0.4, 0.4],
    G**(1/8): [-0.4, 0.5],
    G**(1/4): [-0.4, 0.7],
    G**(3/8): [-0.4, 1.4],
    ((G**0.5) - EPSILON): [-0.4, 5.3],
    ((G**0.5) + EPSILON): [1.2, float("inf")],
    G**1: [16.6, float("inf")],
    G**2: [40.5, float("inf")],
    G**3: [60, float("inf")],
    G**4: [70, float("inf")]
}  

# Límites de aceptación de la atenuación relativa para bandas de octava (clase 2)
ACCEPTANCE_LIMITS_CLASS2= {
    G**-4: [60, float("inf")],
    G**-3: [54, float("inf")],
    G**-2: [39.5, float("inf")],
    G**-1: [15.6, float("inf")],
    ((G**-0.5) - EPSILON): [0.8, float("inf")],
    ((G**-0.5) + EPSILON): [-0.6, 5.8],
    G**(-3/8): [-0.6, 1.7],
    G**(-1/4): [-0.6, 0.9],
    G**(-1/8): [-0.6, 0.7],
    1: [-0.6, 0.6],
    G**(1/8): [-0.6, 0.7],
    G**(1/4): [-0.6, 0.9],
    G**(3/8): [-0.6, 1.7],
    ((G**0.5) - EPSILON): [-0.6, 5.8],
    ((G**0.5) + EPSILON): [0.8, float("inf")],
    G**1: [15.6, float("inf")],
    G**2: [39.5, float("inf")],
    G**3: [54, float("inf")],
    G**4: [60, float("inf")]
} 
