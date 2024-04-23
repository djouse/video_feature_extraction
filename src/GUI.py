import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from scenedetect import detect, ContentDetector
import visbeat3 as vb
from media_source import SourceMedia
import os

from setup import args

def frame_to_sec(frame, fps):
    return (float)(frame/fps) #seconds = frame/fps
def sec_to_frame(second, fps):
    return second*fps #frame = second*fds

#def     

RESOLUTION = 1
video = args.video
video_dir = args.video_360p_dir
video_path = os.path.join(video_dir, video)
video = os.path.basename(video_path)

npz = np.load("flow/" + video.replace('.mp4', '.npz'), allow_pickle=True)
flow_magnitude_list = npz['flow']
flow = np.asarray(flow_magnitude_list)
frame_count =0


class VideoGUI(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.initUI()

    def initUI(self):
        # Set up the layout
        layout = QGridLayout()
        self.setLayout(layout)

        # Create QLabel widget for video
        self.video_label = QLabel(self)
        layout.addWidget(self.video_label, 0, 0)

        # Open the video file
        self.video_capture = cv2.VideoCapture(self.video_path)

        # Check if the video file opened successfully
        if not self.video_capture.isOpened():
            print("Error: Unable to open video file.")
            exit()

        # Get scene cuts
        self.scene_list = detect(self.video_path, ContentDetector())

        # Timer for updating the video frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(25)  # Update every 25 milliseconds

        # Placeholder for the previous frame
        self.prev_frame = None

        # Variables to store magnitude data for plotting
        self.magnitude_data = []
        self.frame_count = 0

        # Create the figure and canvas for magnitude plot
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, 0, 1)

        # Animation function for updating the plot
        self.anim = FuncAnimation(self.fig, self.update_magnitude_plot, interval=25)

    def update_frame(self):
        # Read a frame from the video
        ret, frame = self.video_capture.read()

        # If frame reading was unsuccessful, stop the timer
        if not ret:
            self.timer.stop()
            return

        # Process the frame and compute optical flow
        if self.prev_frame is not None:
            self.magnitude_data.append(flow[self.frame_count])
            self.frame_count+=1
            # Append magnitude data for plotting

        # Convert the frame to QImage
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        video_qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display the video frame
        self.video_label.setPixmap(QPixmap.fromImage(video_qimage))

        # Save current frame for the next iteration
        self.prev_frame = frame.copy()

    def update_magnitude_plot(self, frame):
        # Clear previous plot
        self.ax.clear()

        # Plot magnitude data
        self.ax.plot(range(len(self.magnitude_data)), self.magnitude_data, color='blue')
        self.ax.set_xlabel('Frame')
        self.ax.set_ylabel('Magnitude')
        self.ax.set_title('Optical Flow Magnitude')
        self.ax.set_ylim(0, 5)  # Adjust y-axis limit if needed

        # Draw vertical lines corresponding to scene cuts
        scene_counter = 0
        for scene in self.scene_list:
            if frame >= scene[0].get_frames():
                self.ax.axvline(x=scene[0].get_frames(), color='red', linestyle='--', linewidth=1)

        # Draw the plot
        self.canvas.draw()

if __name__ == '__main__':
    source = SourceMedia()
    vb.Video.getVisualTempo = vb.Video_CV.getVisualTempo
    video_path = source.getTestVideo()

    video = os.path.basename(video_path)
    vlog = vb.PullVideo(name=video, source_location=video_path, max_height=360)
    vbeats = vlog.getVisualBeatSequences(search_window=None)[0]

    tempo, beats = vlog.getVisualTempo()
    print("Tempo is", tempo)
    vbeats_list = []
    for vbeat in vbeats:
        i_beat = round(vbeat.start / 60 * tempo * 4)
        vbeat_dict = {
            'start_time': vbeat.start,
            'bar'       : int(i_beat // 16),
            'tick'      : int(i_beat % 16),
            'weight'    : vbeat.weight
        }
        if vbeat_dict['tick'] % RESOLUTION == 0:  # only select vbeat that lands on the xth tick
            vbeats_list.append(vbeat_dict)
    print('%d / %d vbeats selected' % (len(vbeats_list), len(vbeats)))
    
    source = SourceMedia()
    app = QApplication(sys.argv)
    gui = VideoGUI(video_path)
    gui.setWindowTitle('Video with Optical Flow and Magnitude Graph')
    gui.show()
    sys.exit(app.exec_())
