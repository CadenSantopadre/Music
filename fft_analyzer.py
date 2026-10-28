import numpy as np

def calculate_fft(pcm_data, sample_rate=44100, n_bars=32):
    """
    Convert stereo, signed 16-bit PCM audio into balanced FFT bar magnitudes.
    Returns a list of n_bars values between 0.0 and 1.0.
    """
    samples = np.frombuffer(pcm_data, dtype=np.int16)
    if len(samples) < 2:
        return [0.0] * n_bars

    samples = samples.ravel()
    if len(samples) % 2 != 0:
        samples = samples[:-1]

    samples = samples.reshape(-1, 2).astype(np.float32)
    samples = samples.mean(axis=1)

    if len(samples) < 2:
        return [0.0] * n_bars

    samples -= samples.mean()
    window = np.hanning(len(samples))
    windowed = samples * window
    spectrum = np.abs(np.fft.rfft(windowed))
    spectrum /= max(window.sum() / 2, 1e-8)

    frequencies = np.fft.rfftfreq(len(samples), d=1 / sample_rate)

    # 1. SHIFT FREQUENCY BOUNDARIES: 
    # Raising min_freq to 60Hz drops sub-bass mud. Lowering max_freq to 12000Hz 
    # ignores "air" frequencies that commercial songs rarely push hard.
    min_freq = 60
    max_freq = 12000

    edges = np.geomspace(min_freq, max_freq, n_bars + 1)
    bars = []

    for i in range(n_bars):
        low = np.searchsorted(frequencies, edges[i])
        high = np.searchsorted(frequencies, edges[i + 1])
        high = max(high, low + 1)
        high = min(high, len(spectrum))

        band = spectrum[low:high]

        if len(band) == 0:
            magnitude = 0.0
        else:
            # 2. COMBINATION CALCULATOR (Best of both worlds):
            # Pure 'mean' empties the treble. Pure 'max' overloads the bass.
            # Mixing them creates an even energy spread across wide bands.
            magnitude = (np.max(band) * 0.4) + (np.mean(band) * 0.6)

        # 3. EQUALIZATION BOOST (Treble Equalizer):
        # Naturally, music has much less energy in high frequencies than low frequencies.
        # This progressively multiplies the volume of higher bars to match the bass.
        treble_boost = 1.0 + (i / n_bars) * 2.5
        magnitude *= treble_boost

        db = 20 * np.log10(magnitude + 1e-8)
        db_full_scale = db - 90.3

        # 4. CALIBRATED RANGE:
        # Changed the baseline. Instead of compressing into a tiny window, 
        # we look from -45 dBFS up to -5 dBFS. This prevents normal tracks 
        # from hitting the ceiling instantly.
        normalized = (db_full_scale + 45) / 40
        normalized = np.clip(normalized, 0.0, 1.0)

        bars.append(float(normalized))

    return bars
