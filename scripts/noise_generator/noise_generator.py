import argparse
import wave
import sys
from pathlib import Path
import numpy as np

# Añadir el directorio scripts al path para importar config
SCRIPT_DIR = Path(__file__).resolve().parent  # Directorio actual del script
sys.path.append(str(SCRIPT_DIR.parent))  # Subir un nivel para importar config

from config import SAMPLE_RATE


# ==============================
# CONSTANTES DE CALIBRACIÓN
# ==============================

FULL_SCALE = 32767        # 0 dBFS en int16
TARGET_DBFS = -18        # Nivel RMS objetivo (estándar audio)
TARGET_RMS = FULL_SCALE * (10 ** (TARGET_DBFS / 20))


# ==============================
# RUTA DEL PROYECTO PARA GUARDAR LOS ARCHIVOS DE AUDIO GENERADOS
# ==============================

# Estructura (simplificada) esperada:
# TFG_SAMUEL/
# ├─ data/
# .
# .
# .
# └─ scripts/
#    .
#    .
#    └─ noise_generator/
#       └─ noise_generator.py

PROJECT_ROOT = SCRIPT_DIR.parent.parent  # Subir dos niveles para llegar a la raíz del proyecto (TFG_SAMUEL)
DATA_DIR = PROJECT_ROOT / "data"  # Directorio donde se guardarán los archivos de audio generados

# Crear la carpeta data si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)


class NoiseGenerator:

    @staticmethod
    def generate_white_noise(duration, sample_rate=SAMPLE_RATE):
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

        # Normalización por RMS
        rms = np.sqrt(np.mean(white_noise ** 2))
        white_noise *= TARGET_RMS/rms
        
        # Protección frente a picos
        white_noise = np.clip(white_noise, -FULL_SCALE, FULL_SCALE)
        
        return white_noise.astype(np.int16)

    @staticmethod
    def generate_pink_noise(duration, sample_rate=SAMPLE_RATE):
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

        # Factor de escala para cada bin de frecuencia, creando así ruido rosa (-3 dB/octava)
        factor_scale = np.zeros_like(frequency_bins)
        factor_scale[1:] = 1 / (np.sqrt(frequency_bins[1:]))

        # Escalo la FFT del ruido blanco con el factor calculado
        pink_noise_fft = white_noise_fft * factor_scale

        # Inversa de la FFT del ruido rosa para conseguirlo en el dominio temporal
        pink_noise = np.fft.irfft(pink_noise_fft)
        
        # Normalización por RMS
        rms = np.sqrt(np.mean(pink_noise ** 2))
        pink_noise *= TARGET_RMS/rms
        
        # Protección frente a picos
        pink_noise = np.clip(pink_noise, -FULL_SCALE, FULL_SCALE)

        return pink_noise.astype(np.int16)
    
    @staticmethod
    def save_to_wav(signal, output_path, sample_rate=SAMPLE_RATE):
        """
        Guarda una señal de audio en un archivo WAV con formato 16 bits.
        
        Args:
            output_path (str | Path): Ruta del archivo WAV a guardar.
            signal (np.ndarray): Señal de audio a guardar.
            sample_rate (int): Frecuencia de muestreo en Hz.
        """
        output_path = Path(output_path)  # Asegurar que es un objeto Path
        
        # Guardar la señal en formato WAV con 16 bits por muestra
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16 bits = 2 bytes
            wav_file.setframerate(sample_rate)  # Frecuencia de muestreo
            wav_file.writeframes(signal.tobytes())  # Escribir los datos de audio en el archivo
            
    @classmethod
    def generate_and_save(cls, noise_type, duration, output_filename):
        """Genera ruido (blanco o rosa) y lo guarda en un archivo WAV.

            Args:
                noise_type (str): "white" o "pink".
                duration (float): Duración en segundos.
                output_filename (str | Path | None): Nombre del archivo de salida. Si es None, se guarda en /data.

            Returns:
                tuple[np.ndarray, Path]: Señal generada y ruta del archivo guardado.
        
        """
        if noise_type == "white":
            signal = cls.generate_white_noise(duration)
        elif noise_type == "pink":
            signal = cls.generate_pink_noise(duration)
        else:
            raise ValueError("Tipo de ruido no soportado. Use 'white' o 'pink'.")

        # Determinar la ruta de salida
        if output_filename is None:
            # Si no se proporciona un nombre de archivo, se guarda en la carpeta data con un nombre basado en el tipo de ruido y duración
            output_path = DATA_DIR / f"{noise_type}_noise_{duration:.1f}s.wav"
        else:
            # Si se proporciona un nombre de archivo, se guarda en la ruta especificada
            output_path = Path(output_filename)

        # Guardar el archivo WAV
        cls.save_to_wav(signal, output_path)

        return signal, output_path
    
    
    
def parse_args():
    """ Parsea los argumentos de la línea de comandos para generar ruido.
        Permite especificar el tipo de ruido, duración y nombre del archivo de salida.
    """
    
    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Generador de ruido blanco o rosa y exportación a WAV.")
    
    # Argumento para el tipo de ruido a generar (blanco o rosa)
    parser.add_argument(
        "--type",
        choices=["white", "pink"],
        required=True,
        help="Tipo de ruido a generar: 'white' para ruido blanco, 'pink' para ruido rosa."
    )
    
    # Argumento para la duración del ruido en segundos
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Duración del ruido en segundos (ejemplo: 5)."
    )
    
    # Argumento opcional para el nombre del archivo de salida
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Nombre del archivo de salida (ejemplo: 'white_noise.wav'). Si no se especifica, se guardará en la carpeta data con un nombre basado en el tipo de ruido y duración."
    )
    
    return parser.parse_args()  # Devuelve un objeto con los argumentos parseados


if __name__ == "__main__":
    try:
        args = parse_args()  # Parsear los argumentos de la línea de comandos
        signal, output_path = NoiseGenerator.generate_and_save(args.type, args.duration, args.output)  # Generar y guardar el ruido
        print(f"Ruido {args.type} generado y guardado en: {output_path}")  # Imprimir la ruta del archivo guardado
    except SystemExit:
        # Si faltan argumentos, mostrar una guía personalizada
        print("\nGuía de uso del generador de ruido:")
        print("Este script genera ruido blanco o rosa y lo guarda en un archivo WAV.")
        print("\nArgumentos requeridos:")
        print("  --type     Tipo de ruido: 'white' para ruido blanco, 'pink' para ruido rosa.")
        print("  --duration Duración del ruido en segundos (ejemplo: 5).")
        print("\nArgumentos opcionales:")
        print("  --output   Nombre del archivo de salida (ejemplo: 'white_noise.wav').")
        print("             Si no se especifica, se guardará en la carpeta data con un nombre automático.")
        print("\nEjemplos de uso:")
        print("  python noise_generator.py --type white --duration 10")
        print("  python noise_generator.py --type pink --duration 5 --output mi_ruido.wav")
        print("\nEjecuta el script desde el directorio scripts/noise_generator/ o ajusta la ruta según corresponda.")