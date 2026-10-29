# Music Player

This Music Player is a PyQt music player that plays downloaded music stored in a json directory while showing audio spectrum visualization, beat-predictions, and controls using a simple layout.

---

### Features
* **Real-time Spectrum Analysis:** FFT-based audio visualizer built right into the window
* **JSON-backed Library:** Simple, portable `music_files.json` file to manage tracks, playlists, and metadata.
* **Offline Playback:** Optimized for playing local audio files (MP3 Only) with minimal CPU overhead.

---

### Getting Started

#### Prerequisites
Ensure your venv has the following dependancies:
* numpy
* pyaudio
* PyQt6
* miniaudio

#### Installation

The repo comes with a shell script `music_player.sh` to employ along with a bash script to make an executable desktop shortcut

Use this bash script in the desktop to run it:
~~~
[Desktop Entry]
Type=Application
Name=My Music App
Comment=Launch Python script with venv
Exec=/home/cadensantopadre/VSCode/MusicPlayer/music_player.sh
Path=/home/cadensantopadre/VSCode/MusicPlayer/
Icon=/home/cadensantopadre/Pictures/Music.jpg
Terminal=false
StartupNotify=false
~~~

---

### Configuration & Library Format

The app scans your downloaded tracks and maps them using a local `music_files.json` file. Place this file in the project folder's root.

~~~json
{
    "music_files": [
        {
            "path": "music_files/Holiday.mp3",
            "title": "Holiday"
        },
    ]
}
~~~

---

TODO:
* Beat visualization
* JSON custimization in-app
* Reordering and playlists