import sys
import json
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QStackedWidget
from audio_engine import AudioWorker
from miniplayer_view import MiniplayerView
from spectrum_view import SpectrumView
from playlist_view import PlaylistView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Waggle's Music Player")
        self.setGeometry(100, 100, 500, 400)

        self.playlist = []
        self.current_song_index = 0
        self.prev_song_index = 0
        
        self.load_json("songs.json")
        self.init_player()
        self.init_ui()

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.playlist = data["music_files"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("JSON not working!!! Using mock data fallback.")
            self.playlist = [{"title": "Demo Song", "path": "mock.mp3"}]

    def init_player(self):
        self.audio_worker = None
        self.is_playing = False

        if self.playlist:
            self.load_current_song()

    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)

        nav_layout = QHBoxLayout()
        self.btn_mini = QPushButton("Miniplayer")
        self.btn_eq = QPushButton("Spectrum")
        self.btn_whole = QPushButton("Playlist")
        
        nav_layout.addWidget(self.btn_mini)
        nav_layout.addWidget(self.btn_eq)
        nav_layout.addWidget(self.btn_whole)
        main_layout.addLayout(nav_layout)

        self.view_stack = QStackedWidget()
        main_layout.addWidget(self.view_stack)

        # Set up view references
        self.mini_view = MiniplayerView(self)
        self.eq_view = SpectrumView(self)
        self.whole_view = PlaylistView(self)

        self.view_stack.addWidget(self.mini_view)
        self.view_stack.addWidget(self.eq_view)
        self.view_stack.addWidget(self.whole_view)

        self.btn_mini.clicked.connect(lambda: self.view_stack.setCurrentIndex(0))
        self.btn_eq.clicked.connect(lambda: self.view_stack.setCurrentIndex(1))
        self.btn_whole.clicked.connect(lambda: self.view_stack.setCurrentIndex(2))

    def load_qss(self, file_name):
        try:
            with open(file_name, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Warning: Stylesheet {file_name} not found.")

    def handle_repeat_click(self):
        if self.mini_view.shuffle.isChecked():
            self.mini_view.shuffle.setChecked(False)

    def handle_shuffle_click(self):
        if self.mini_view.repeat.isChecked():
            self.mini_view.repeat.setChecked(False)

    def start_playback(self):
        if not self.playlist:
            return

        # Stop any existing playback before starting another song.
        if self.audio_worker is not None:
            if self.audio_worker.isRunning():
                self.audio_worker.stop()
                self.audio_worker.wait()
            self.audio_worker = None

        current_song = self.playlist[self.current_song_index]
        self.audio_worker = AudioWorker(current_song["path"])
        self.audio_worker.spectrum_ready.connect(
            self.mini_view.spectrum.set_spectrum
        )
        self.audio_worker.spectrum_ready.connect(
            self.eq_view.spectrum.set_spectrum
        )

        # Core playback control signals
        self.audio_worker.track_ended.connect(self.handle_end_song)
        self.audio_worker.playback_error.connect(self.handle_playback_error)

        # UI Progress & Duration pipeline updates
        self.audio_worker.duration_changed.connect(self.update_duration)
        self.audio_worker.position_changed.connect(self.update_position)

        # Pass active volume settings down to the new worker immediately
        self.handle_volume_slide()

        self.audio_worker.start()

        self.is_playing = True
        self.mini_view.play.setText("Pause")

    def handle_playback_error(self, message):
        self.is_playing = False
        self.mini_view.play.setText("Play")
        print(f"Audio playback error: {message}")

    def handle_play_click(self):
        if self.audio_worker is not None and self.audio_worker.isRunning():
            if self.is_playing:
                self.audio_worker.pause()
                self.is_playing = False
                self.mini_view.play.setText("Play")
            else:
                self.audio_worker.resume()
                self.is_playing = True
                self.mini_view.play.setText("Pause")
        else:
            self.start_playback()

    def handle_volume_slide(self):
        if self.audio_worker is not None:
            vol = self.mini_view.volume.value()
            # Send scaling integer down to the modern audio worker safely
            self.audio_worker.set_volume(vol)

    def handle_song_slide(self, position):
        if self.audio_worker is not None:
            # Passes user slider drag events to the stream seek layout
            self.audio_worker.seek(position)

    def update_position(self, position):
        self.mini_view.song_progress.blockSignals(True)
        self.mini_view.song_progress.setValue(position)
        self.mini_view.song_progress.blockSignals(False)

    def update_duration(self, duration):
        self.mini_view.song_progress.setRange(0, duration)

    def handle_end_song(self):
        if not self.playlist:
            return

        self.is_playing = False
        self.prev_song_index = self.current_song_index

        if self.mini_view.repeat.isChecked():
            self.start_playback()
            return

        if self.mini_view.shuffle.isChecked() and len(self.playlist) > 1:
            old_index = self.current_song_index
            while self.current_song_index == old_index:
                self.current_song_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_song_index += 1
            if self.current_song_index >= len(self.playlist):
                self.current_song_index = 0

        self.load_current_song()
        self.start_playback()

    def load_current_song(self):
        if not self.playlist:
            return
        current_song = self.playlist[self.current_song_index]
        self.setWindowTitle(f"Playing: {current_song['title']}")

    def handle_next_click(self):
        if not self.playlist:
            return
        self.prev_song_index = self.current_song_index
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.load_current_song()
        self.start_playback()

    def handle_prev_click(self):
        if not self.playlist:
            return
        
        self.prev_song_index = self.current_song_index
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.load_current_song()
        self.start_playback()

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
