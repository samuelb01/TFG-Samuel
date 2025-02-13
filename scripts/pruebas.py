# Script para pruebas

from filters4 import octaveFilter, thirdOctaveFilter, verify_filter_compliance, plot_filter_response, plot_filtered_signals, create_acceptance_limits_dicc
from noise_generator import generate_white_noise, generate_pink_noise

print(int(4.9))

entry_time = ""

entry_time = float("4.9")
print(entry_time)

if isinstance(entry_time, float) or isinstance(entry_time, int):  # Tipo float o int
    print(type(entry_time))

# white = generate_white_noise(5, 48000)
# pink = generate_pink_noise(5, 48000)
# combined_signal, band_levels, fm, fl_selected_bands, fh_selected_bands = (
#     octaveFilter(pink, 48000)
#     # octaveFilter(pink, 48000, selected_bands=[31.5, 2000])
# )

# verify_filter_compliance(48000, fl_selected_bands, fh_selected_bands, "1/1")
# plot_filter_response(48000, fl_selected_bands, fh_selected_bands)
# plot_filtered_signals(combined_signal)
# # plot_filtered_signals(pink)