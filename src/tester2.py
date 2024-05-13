import os
import time
import cv2
import pygame as pg

class Bpm:
    def __init__(self):
        self.space_between_beats = 0.5
        self.last_press = time.time()
        self.bpm = 100
        self.times = []
        self._last_update = time.time()
        self._elapsed_time = 0.0
        self._last_closeness = 1.0
        self.on_beat = 0
        self.beat_num = 0
        self.finished_beat = 0
        self.first_beat = 0
        self.started_beat = 0

    def update(self):
        the_time = time.time()
        self._elapsed_time += the_time - self._last_update
        self._last_update = the_time

        space_between_beats = 60.0 / self.bpm
        since_last_beat = the_time - self.on_beat

        self.finished_beat = self.on_beat and (since_last_beat > 0.1)
        if self.finished_beat:
            self.on_beat = 0

        closeness = self._elapsed_time % space_between_beats
        if closeness < self._last_closeness:
            self.on_beat = the_time
            self.finished_beat = 0
            self.beat_num += 1
            self.started_beat = 1
            self.first_beat = not (self.beat_num % 4)
        else:
            self.started_beat = 0

        self._last_closeness = closeness

def main():
    pg.init()
    going = True
    bpm = Bpm()
    clock = pg.time.Clock()
    sound = pg.mixer.Sound("metronome_tick.mp3")

    # Video setup
    video_path = "../videos/video.mp4"
    video_capture = cv2.VideoCapture(video_path)
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    pg.display.set_caption("Video with Metronome")
    screen = pg.display.set_mode((frame_width, frame_height))

    while going:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False

        # Read a frame from the video
        ret, frame = video_capture.read()
        if not ret:
            break

        # Display the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pg.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))

        # Update the BPM
        bpm.update()

        # Play the metronome sound
        if bpm.started_beat:
            sound.play()

        pg.display.flip()
        clock.tick(30)

    video_capture.release()
    pg.quit()

if __name__ == '__main__':
    main()
