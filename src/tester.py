import sys
import os
import time
import pygame as pg
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

def average_bpm(times):
    """ For the list of times(seconds since epoch) return
        the average beats per minute.
    """
    spaces = []
    previous = times[0]
    for t in times[1:]:
        spaces.append(t - previous)
        previous = t
    avg_space = sum(spaces) / len(spaces)
    return 60.0 / avg_space



class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Player')

        # Create a label to display the video
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        # Create a layout and add the video label to it
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        self.setLayout(layout)

        # Load the video file
        self.load_video()

        # Start the timer to update the video frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // self.fps)  # Update every frame based on the video's frame rate

    def load_video(self):
        # Open a file dialog to select the video file
        if(os.path.exists(os.path.join("..", "videos", "video.mp4"))):
            video_file = os.path.join("..", "videos", "video.mp4")
        else:
            video_file, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
            if not video_file:
                sys.exit()

        # Open the video file using OpenCV
        self.video_capture = cv2.VideoCapture(video_file)

        # Get video properties
        self.width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))

        # Set the window size to match the video dimensions
        self.setFixedSize(self.width, self.height)

    def update_frame(self):
        # Read a frame from the video
        ret, frame = self.video_capture.read()

        # If frame reading was unsuccessful, stop the timer
        if not ret:
            self.timer.stop()
            return

        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a QImage
        image = QImage(frame, frame.shape[0], frame.shape[1], QImage.Format_RGB888)

        # Display the frame on the video label
        self.video_label.setPixmap(QPixmap.fromImage(image))

        # Play metronome sound
        self.play_metronome_sound()

    def play_metronome_sound(self):
        # Play a metronome sound every second
        if self.timer.isActive():
            pygame.mixer.Sound('metronome_tick.mp3').play()

    def closeEvent(self, event):
        # Clean up resources when the window is closed
        self.video_capture.release()
        pg.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
