import numpy as np
import wave
import acoustics.generator as generator

# Parámetros de generación
sample_rate = 48000  # Frecuencia de muestreo
duration = 10        # Duración en segundos
N = sample_rate * duration  # Número de muestras
state = np.random.RandomState(42)  # Usar np.random.RandomState para el estado

# Generar ruido blanco con un estado fijo
white_noise = generator.noise(N, color='white', state=state)

# Generar ruido rosa con el mismo estado
pink_noise = generator.noise(N, color='pink', state=state)

# Función para guardar el audio como archivo WAV
def save_wav(filename, data, sample_rate):
    with wave.open(filename, 'wb') as wav_file:
        n_channels = 1  # Mono
        sampwidth = 2   # 2 bytes por muestra (16-bit)
        n_frames = len(data)
        
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        wav_file.setnframes(n_frames)
        
        # Convertir los datos a un formato de 16-bit PCM
        data = np.int16(data * 32767)
        wav_file.writeframes(data.tobytes())

# Guardar los archivos WAV
save_wav('ruido_blanco_con_state.wav', white_noise, sample_rate)
save_wav('ruido_rosa_con_state.wav', pink_noise, sample_rate)
