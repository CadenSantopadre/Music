from PyQt6.QtWidgets import QWidget, QVBoxLayout

from spectrum_widget import SpectrumWidget


class EqualizerView(QWidget):
    def __init__(self, parent=None, n_bars=32):
        super().__init__(parent)

        self.spectrum = SpectrumWidget(self, n_bars=n_bars)
        layout = QVBoxLayout(self)
        layout.addWidget(self.spectrum)

    def set_spectrum(self, levels):
        self.spectrum.set_spectrum(levels)
