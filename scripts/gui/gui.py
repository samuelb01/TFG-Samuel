from noise.noise_generator import NoiseGenerator
from filter.filter import Filter


class GUI:
    def __init__(self):
        self.noise_generator = NoiseGenerator()
        self.filter = Filter()

    def apply_filter(self):
        self.filter.signal = self.noise_generator.generate_pink_noise(duration=60)
        self.filter.third_octave_filter()
        # self.filter.plot_filtered_signal_levels()
        # self.filter.plot_filter_response()
        self.filter.verify_filter_compliance()