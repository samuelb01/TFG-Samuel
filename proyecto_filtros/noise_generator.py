import numpy as np

def generate_white_noise(duration, sample_rate):
    """
    Genera ruido blanco.
    
    Args:
        duration (float): Duración del ruido en segundos.
        sample_rate (int): Frecuencia de muestreo en Hz.

    Returns:
        np.ndarray: Señal de ruido blanco.
    """
    # Número de muestras
    num_samples = int(duration * sample_rate)

    # Generar ruido blanco con valores aleatorios con una distribución normal estándar (media = 0, desviación estándar = 1)
    white_noise = (np.random.randn(num_samples))

    # Normalizo para un rango de 16-bits
    white_noise *= 32767 / np.max(np.abs(white_noise))
    
    return white_noise.astype(np.int16)

def generate_pink_noise(duration, sample_rate):
    """
    Genera ruido rosa.
    
    Args:
        duration (float): Duración del ruido en segundos.
        sample_rate (int): Frecuencia de muestreo en Hz.

    Returns:
        np.ndarray: Señal de ruido rosa.
    """

    # Número de muestras
    num_samples = int(duration * sample_rate)

    # Genero ruido blanco
    white_noise = np.random.randn(num_samples)

    # FFT del ruido blanco
    white_noise_fft = np.fft.rfft(white_noise)

    # Calculo los bins de frecuencia (representan rangos de frecuencia en la señal)
    frequency_bins = np.fft.rfftfreq(num_samples, d=1/sample_rate)

    # Factor de escala para cada bin de frecuencia, creando así ruido rosa
    factor_scale = np.zeros_like(frequency_bins)
    factor_scale[1:] = 1 / (np.sqrt(frequency_bins[1:]))

    # Escalo la FFT del ruido blanco con el factor calculado
    pink_noise_fft = white_noise_fft * factor_scale

    # Inversa de la FFT del ruido rosa para conseguirlo en el dominio temporal
    pink_noise = np.fft.irfft(pink_noise_fft)
    
    # Normalizo para un rango de 16-bits
    pink_noise *= 32767 / np.max(np.abs(pink_noise))
    
    return pink_noise.astype(np.int16)