from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush


class SpectrumWidget(QWidget):
    def __init__(self, parent=None, n_bars=32):
        super().__init__(parent)

        self.n_bars = n_bars

        self.target_levels = [0.0] * n_bars
        self.display_levels = [0.0] * n_bars

        self.setMinimumHeight(100)

        # Update the visualizer at approximately 60 FPS.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def set_spectrum(self, levels):
        self.target_levels = list(levels[:self.n_bars])

        # Pad the list if fewer values are received.
        self.target_levels += [
            0.0
        ] * (self.n_bars - len(self.target_levels))

    def animate(self):
        # Smoothly approach the latest FFT values.
        for i in range(self.n_bars):
            target = self.target_levels[i]
            current = self.display_levels[i]

            if target > current:
                # Bars rise quickly.
                self.display_levels[i] += (
                    target - current
                ) * 0.65
            else:
                # Bars fall more gradually.
                self.display_levels[i] += (
                    target - current
                ) * 0.18

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            QColor("#151515")
        )

        width = self.width()
        height = self.height()

        gap = 3
        bar_width = max(
            1,
            (width - gap * (self.n_bars - 1)) / self.n_bars
        )

        for i, level in enumerate(self.display_levels):
            bar_height = level * height * 0.9

            x = i * (bar_width + gap)
            y = height - bar_height

            # Simple vertical color gradient.
            color_position = i / max(self.n_bars - 1, 1)

            red = int(50 + 180 * color_position)
            green = int(220 - 100 * color_position)
            blue = 255

            painter.setBrush(
                QBrush(QColor(red, green, blue))
            )

            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawRoundedRect(
                int(x),
                int(y),
                int(bar_width),
                max(1, int(bar_height)),
                2,
                2
            )

        painter.end()