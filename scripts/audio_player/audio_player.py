import threading
import pyaudio
import numpy as np
from config import SAMPLE_RATE

class AudioPlayer:
    """ Clase para reproducir audio en tiempo real """

    def __init__(self):
        self.noise_thread = None
        self.control_noise_event = threading.Event()

    def start_noise_thread(self, signal_to_play):
        """ Inicia un hilo para reproducir el audio """
        # Varificar si el hilo ya se encuentra en ejecución, si es así se detiene
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
                signal_to_play
            ):  # Mientras el evento no esté activado
                end = start + chunk  # Fin de la reproducción
                stream.write(
                    signal_to_play[start:end].astype(np.int16).tobytes()
                )  # Reproducir audio
                start = end  # Actualizar inicio de la reproducción

        finally:
            stream.stop_stream()  # Detener stream
            stream.close()  # Cerrar stream
            p.terminate()  # Cerrar PyAudio