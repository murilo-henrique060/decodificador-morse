import numpy as np

def filter_frequencies(data, rate, low_cutoff, high_cutoff):
    # 1. FFT
    fft_data = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1.0/rate)
    
    # 2. Create mask for frequency range (Bandpass example)
    mask = (freqs >= low_cutoff) & (freqs <= high_cutoff)
    
    # 3. Apply mask (Zero out frequencies outside range)
    fft_data_filtered = fft_data * mask
    
    # 4. Inverse FFT
    new_audio = np.fft.irfft(fft_data_filtered)
    
    return new_audio.astype(np.int16)