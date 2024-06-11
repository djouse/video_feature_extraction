""" 

Project Overview
----------------

    This code intends to:
        1 - Have an input directory to store videos, 
        2 - Have a logger to run experiments on
        3 - Convert specified video to convert to 360p, stored in another directory 
        4 - Have two separate functionalities to process the intended video: 
            a) Have a GUI to see processed frames, the optical flow, motion saliency, and the video beats TODO
            b) Have a plotter that returns graphs for the specified video on optical flow, motion salency and beat information TODO
        5 - After having the main features retrieved following 3b) there is the need to:
            a) First, add a methronome or a signal to the 1 in the beat  TODO
            b) Then, add generated music to the beat with MIDI  TODO

Retrieved Features
------------------

    This code retrieves the following video information:
        - optical flow
        - motion saliency
        - timing information (beat-time mapping)
    
Classes
-------
    GUI: Widget to view the information on 4a)
    Plotter: Mathplotlib graph generator for the different information

"""


import logging 

from setup import args
from video_processor import videoProcessor

logger = logging.getLogger(__name__)

class Runner(): 
    def __init__(self) -> None:
        self.video = args.video
        self.video_dir = args.video_360p_dir
        self.optical_flow_method = args.optical_flow_method
        self.useGUI = args.gui
        logger.info("Runner Initialized")

    def run(self):
        if not self.useGUI:
            # Start threads to run the specified methods concurrently
            logger.debug("Using Graphical Plots.\nTo use GUI parse --gui argument")
            logger.info("Processing video...")

            video = videoProcessor(self.video, self.video_dir)
            
            video.getOpticalFlow(self.optical_flow_method)
            video.getVideoBeat()
            video.getSceneCuts()
            video.saveFeatures()
            logger.info("DONE processing video.")
    

if __name__ == '__main__':
    runner = Runner()
    runner.run()
    logger.info("Exiting.")