import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QAbstractItemView

class ListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = "songs.json"


        self.playlist = []
        self.data = self.load_json(self.filename)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        layout.addWidget(self.list_widget)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.save)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)
        self.load_titles()


    def load_json(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.playlist = data["music_files"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("JSON not working!!! Using mock data fallback.")
            self.playlist = [{"title": "Demo Song", "path": "music_files/Demo.mp3"}]

    def load_titles(self):
        for song in self.playlist:
            self.list_widget.addItem(song["title"])

    def save(self):
        reordered = []
        for i in range(self.list_widget.count()):
            item_text = self.list_widget.item(i).text()
            
            original_path = ""
            for song in self.playlist:
                if song["title"] == item_text:
                    original_path = song["path"]
                    break
            
            reordered.append({"title": item_text, "path": original_path})
        
        self.playlist = reordered

        # --- ADD THIS LOGIC TO ACTUALLY WRITE THE FILE ---
        output_data = {"music_files": self.playlist}
        try:
            with open(self.filename, "w") as f:
                json.dump(output_data, f, indent=4)
            print("Successfully saved reordered playlist to file!")
        except Exception as e:
            print(f"Error saving JSON file: {e}")
