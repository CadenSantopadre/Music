import time
import threading
from PyQt6.QtCore import QThread, pyqtSignal
import pyaudio
from pydub import AudioSegment
from fft_analyzer import calculate_fft


class AudioWorker(QThread):
    track_ended = pyqtSignal() #Send a signal if the traack ends
    playback_error = pyqtSignal(str) #Same here and other signals
    duration_changed = pyqtSignal(int)  # Total length in milliseconds
    position_changed = pyqtSignal(int)  # Current timestamp in milliseconds
    spectrum_ready = pyqtSignal(list) 

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._is_running = True
        self._is_paused = False
        self.stop_event = threading.Event() #When we pause, tell it to turn off play mode

        self._volume_scalar = 1.0
        self._seek_requested_ms = -1

    def run(self):
        try:
            sound = AudioSegment.from_mp3(self.file_path)
            raw_data = sound.raw_data
            
            total_duration_ms = len(sound)
            self.duration_changed.emit(total_duration_ms) #this actually sends the thing for pyqtSignal
            
            p = pyaudio.PyAudio() #inits the pyaudio module
            stream = p.open(#Creates a channel for data to flow through
                format=p.get_format_from_width(sound.sample_width),#bytes per sample 
                channels=sound.channels,
                rate=sound.frame_rate,
                output=True,
                frames_per_buffer=2048 
            )

            bytes_per_ms = (sound.sample_width * sound.channels * sound.frame_rate) / 1000
            chunk_size = 2048 * sound.sample_width * sound.channels
            position = 0

            while position < len(raw_data) and self._is_running:
                if self._is_paused:
                    time.sleep(0.05)
                    continue

                if self._seek_requested_ms != -1:
                    position = int(self._seek_requested_ms * bytes_per_ms)
                    position = (position // chunk_size) * chunk_size
                    self._seek_requested_ms = -1

                chunk = raw_data[position : position + chunk_size]
                
                if self._volume_scalar != 1.0:
                    sound_chunk = AudioSegment(
                        data=chunk, 
                        sample_width=sound.sample_width, 
                        frame_rate=sound.frame_rate, 
                        channels=sound.channels
                    )

                    if self._volume_scalar <= 0.01:
                        chunk = b'\x00' * len(chunk)
                    else:
                        import math
                        db_change = 20 * math.log10(self._volume_scalar)
                        chunk = sound_chunk.apply_gain(db_change).raw_data

                # AudioSegment.raw_data and its slices are already bytes.
                pcm_data = chunk

                # Split the chunk into smaller pieces for more frequent updates.
                bytes_per_frame = 2 * 2  # 2 channels * 2 bytes per sample
                frames_per_update = 2048
                bytes_per_update = frames_per_update * bytes_per_frame

                for start in range(0, len(pcm_data), bytes_per_update):
                    if self.stop_event.is_set():
                        break

                    # Get a smaller piece of audio.
                    audio_chunk = pcm_data[
                        start:start + bytes_per_update
                    ]

                    # Analyze it for the visualizer.
                    bars = calculate_fft(
                        audio_chunk,
                        sample_rate=44100,
                        n_bars=32
                    )

                    # Send the results to the GUI.
                    self.spectrum_ready.emit(bars)

                    # Play the same audio that we analyzed.
                    stream.write(audio_chunk)
                position += chunk_size

                current_ms = int(position / bytes_per_ms)
                self.position_changed.emit(current_ms)

            stream.stop_stream()
            stream.close()
            p.terminate()

            if self._is_running:
                self.track_ended.emit()

        except Exception as e:
            self.playback_error.emit(str(e))

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._is_running = False
        self.stop_event.set()

    def set_volume(self, volume_percent):
        """Called safely from MainWindow's handle_volume_slide (0-100)"""
        self._volume_scalar = max(0.0, min(1.0, volume_percent / 100.0))

    def seek(self, position_ms):
        """Called safely from MainWindow's handle_song_slide"""
        self._seek_requested_ms = position_ms
