from collections import deque
from statistics import mean, pstdev
import time


class BeatDetector:
    def __init__(
        self,
        low_band_count=8,
        history_size=43,
        minimum_flux=0.025,
        sensitivity=1.0,
        cooldown_seconds=0.25,
    ):
        self.low_band_count = low_band_count
        self.minimum_flux = minimum_flux
        self.sensitivity = sensitivity
        self.cooldown_seconds = cooldown_seconds
        self.previous_bands = None
        self.flux_history = deque(maxlen=history_size)
        self.last_beat_time = float("-inf")

    def process(self, bars):
        """Return True when the low-frequency spectrum has a new strong onset."""
        low_bands = [float(value) for value in bars[:self.low_band_count]]
        if not low_bands:
            return False

        if self.previous_bands is None:
            self.previous_bands = low_bands
            return False

        band_count = min(len(low_bands), len(self.previous_bands))
        if band_count == 0:
            self.previous_bands = low_bands
            return False

        flux = sum(
            max(0.0, low_bands[i] - self.previous_bands[i])
            for i in range(band_count)
        ) / band_count
        self.previous_bands = low_bands

        threshold = self.minimum_flux
        if len(self.flux_history) >= 4:
            threshold = max(
                threshold,
                mean(self.flux_history) + self.sensitivity * pstdev(self.flux_history),
            )

        self.flux_history.append(flux)
        now = time.monotonic()
        if flux < threshold or now - self.last_beat_time < self.cooldown_seconds:
            return False

        self.last_beat_time = now
        return True
