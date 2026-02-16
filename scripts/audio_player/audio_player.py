import threading
import pyaudio
import numpy as np
from config import SAMPLE_RATE

class AudioPlayer:
    """ Clase para reproducir audio en tiempo real """

    def __init__(self):
        self.noise_thread = None  # Hilo para reproducir el audio
        self.control_noise_event = threading.Event()  # Evento para controlar el hilo de reproducción

    def start_noise_thread(self, signal_to_play):
        """ Inicia un hilo para reproducir el audio """
        # Verificar si el hilo ya se encuentra en ejecución, si es así se detiene
        self.stop_noise_thread()

        self.control_noise_event.clear()  # Limpiar el evento de control

        # Hilo para reproducir el audio
        self.noise_thread = threading.Thread(
            target=self.play_noise,  # Función a ejecutar por el hilo
            args=(signal_to_play,),  # Argumentos de la función
            daemon=True,  # Hilo se detiene cuando el programa principal se detiene
        )

        self.noise_thread.start()  # Iniciar el hilo

    def stop_noise_thread(self):
        """ Detiene el hilo de reproducción """
        # Si el hilo está activo y en ejecución se detiene
        if self.noise_thread and self.noise_thread.is_alive():
            self.control_noise_event.set()  # Establecer evento de detención en activo
            self.noise_thread.join()  # Esperar a que el hilo termine
            self.noise_thread = None  # Resetar el hilo

    def play_noise(self, signal_to_play):
        """Reproduce el ruido generado"""
        
        # Copiar la señal y asegurar que es float para aplicar el fade
        signal = signal_to_play.copy().astype(np.float64)
        
        # Aplicar Fade-in y Fade-out de 100ms para evitar comienzo y final bruscos
        fade_duration = 0.1  # segundos
        fade_samples = int(fade_duration * SAMPLE_RATE)
        
        if len(signal) > 2 * fade_samples:
            # Rampa ascendente (Fade-in)
            fade_in = np.linspace(0, 1, fade_samples)
            signal[:fade_samples] *= fade_in
            
            # Rampa descendente (Fade-out)
            fade_out = np.linspace(1, 0, fade_samples)
            signal[-fade_samples:] *= fade_out

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
                signal
            ):  # Mientras el evento no esté activado
                end = start + chunk  # Fin de la reproducción
                
                # Obtener el fragmento de audio
                audio_chunk = signal[start:end]
                
                # Clipping para evitar desbordamiento (wrapping) en la conversión a int16
                audio_chunk = np.clip(audio_chunk, -32768, 32767)
                
                stream.write(
                    audio_chunk.astype(np.int16).tobytes()
                )  # Reproducir audio
                start = end  # Actualizar inicio de la reproducción

        finally:
            stream.stop_stream()  # Detener stream
            stream.close()  # Cerrar stream
            p.terminate()  # Cerrar PyAudio