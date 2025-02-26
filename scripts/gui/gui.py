from noise.noise_generator import NoiseGenerator
from filters.filters import Filters


class GUI:
    def __init__(self):
        self.noise_generator = NoiseGenerator()
        self.filters = Filters()

    def filter(self):
        self.filters.octave_filter(self.noise_generator.generate_pink_noise(60, 48000))