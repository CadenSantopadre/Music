from PyQt6.QtWidgets import QWidget, QVBoxLayout

from playlist_widget import ListWidget

class PlaylistView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.playlistWidget = ListWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.playlistWidget)


