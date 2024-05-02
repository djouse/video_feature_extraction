# Video Feature Extraction:
    
    This tool converts videos to 360p and retrieves, optical flow magnitude, scene cuts, estimation of musical tempo using visbeats3, and saves this information for a given video file.

## Retrieved Features
------------------------------------

    This code retrieves the following video information:
        - optical flow
        - motion saliency
        - timing information (beat-time mapping)

## TODO 
------------------------------------
    Multi-Threading in feature retrievel and in video conversion and directory creation

## Project Overview
------------------------------------

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

