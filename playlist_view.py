from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class PlaylistView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("🖥️ Full Media Library")
        label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
        
        layout.addWidget(QLabel("Tracks | Playlists | Albums | Settings"))
