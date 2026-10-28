from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QSlider
from PyQt6.QtCore import Qt

from spectrum_widget import SpectrumWidget


class MiniplayerView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        first_container = QHBoxLayout()
        layout.addLayout(first_container)

        sec_container = QHBoxLayout()
        layout.addLayout(sec_container)

        self.repeat = QCheckBox("Repeat")
        self.shuffle = QCheckBox("Shuffle")
        first_container.addWidget(self.repeat)
        first_container.addWidget(self.shuffle)

        self.play = QPushButton("Play")
        first_container.addWidget(self.play)

        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(75)
        first_container.addWidget(self.volume)

        self.prev = QPushButton("Prev")
        self.song_progress = QSlider(Qt.Orientation.Horizontal)
        self.next = QPushButton("Next")

        sec_container.addWidget(self.prev)
        sec_container.addWidget(self.song_progress)
        sec_container.addWidget(self.next)

        self.spectrum = SpectrumWidget(self)
        layout.addWidget(self.spectrum)

        # Connect slots back to methods handled on the shared parent app instance
        self.repeat.clicked.connect(self.main_app.handle_repeat_click)
        self.shuffle.clicked.connect(self.main_app.handle_shuffle_click)
        self.play.clicked.connect(self.main_app.handle_play_click)
        self.volume.sliderMoved.connect(self.main_app.handle_volume_slide)
        self.prev.clicked.connect(self.main_app.handle_prev_click)
        self.song_progress.sliderMoved.connect(self.main_app.handle_song_slide)
        self.next.clicked.connect(self.main_app.handle_next_click)
