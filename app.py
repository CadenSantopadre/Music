import sys
import json
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
QVBoxLayout, QWidget, QSlider, QHBoxLayout, QCheckBox)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl

class MainWindow(QMainWindow):
    def __init__(self): #Constructor
        super().__init__()
        self.setWindowTitle("My PyQt Application")
        self.setGeometry(100, 100, 400, 300)

        self.load_json("songs.json")
        self.current_song_index = 0
        self.max_songs = 0
        
        self.init_ui()
        self.init_player()

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.playlist = data["music_files"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("JSON not working!!!")

    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        
        layout = QVBoxLayout()
        container.setLayout(layout)

        first_container = QHBoxLayout()
        layout.addLayout(first_container)
        # Adding elements        
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

        self.song_progress = QSlider(Qt.Orientation.Horizontal)

        layout.addWidget(self.song_progress)

        # Adding method connections
        self.repeat.clicked.connect(self.handle_repeat_click)
        self.shuffle.clicked.connect(self.handle_shuffle_click)
        self.play.clicked.connect(self.handle_play_click)
        self.volume.sliderMoved.connect(self.handle_volume_slide)
        self.song_progress.sliderMoved.connect(self.handle_song_slide)

    def init_player(self):
        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        
        self.mediaPlayer.setAudioOutput(self.audioOutput)
        
        current_song = self.playlist[self.current_song_index]
        file_path = current_song["path"] 
        
        self.setWindowTitle(f"Playing: {current_song['title']}")
        
        self.mediaPlayer.setSource(QUrl.fromLocalFile(file_path))

        self.audioOutput.setVolume(0.75)

        self.mediaPlayer.positionChanged.connect(self.update_position)
        self.mediaPlayer.durationChanged.connect(self.update_duration)

        self.mediaPlayer.mediaStatusChanged.connect(self.handle_end_song)

    def handle_repeat_click(self):
        if(self.shuffle.isChecked()):
            self.shuffle.setChecked(False)

    def handle_shuffle_click(self):
        if(self.repeat.isChecked()):
            self.repeat.setChecked(False)

    def handle_play_click(self):
        if(self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState):
            self.mediaPlayer.pause()
            self.play.setText("Play")
        else:
            self.mediaPlayer.play()
            self.play.setText("Pause")

    def handle_volume_slide(self):
        vol = self.volume.value()
        #print(f"Volume is now {vol}")
        self.audioOutput.setVolume(vol/100)

    def handle_song_slide(self, position):
        self.mediaPlayer.setPosition(position)

    def update_position(self, position):
        self.song_progress.setValue(position)

    def update_duration(self, duration):
        self.song_progress.setRange(0, duration)

    def handle_end_song(self, status):
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        
        if self.repeat.isChecked():
            self.mediaPlayer.setPosition(0)
            self.mediaPlayer.play()
            return

        if self.shuffle.isChecked() and len(self.playlist) > 1:
            old_index = self.current_song_index
            while self.current_song_index == old_index:
                self.current_song_index = random.randint(0, len(self.playlist) - 1)
        
        else:
            self.current_song_index += 1
            if self.current_song_index >= len(self.playlist):
                self.current_song_index = 0

        self.load_current_song()
        self.mediaPlayer.play()
        self.play.setText("Pause")

    def load_current_song(self):
        current_song = self.playlist[self.current_song_index]
        file_path = current_song["path"] 
        
        self.setWindowTitle(f"Playing: {current_song['title']}")
        self.mediaPlayer.setSource(QUrl.fromLocalFile(file_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
