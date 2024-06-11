import cv2
import numpy as np
import skvideo.io
import visbeat3 as vb
from scenedetect import detect, ContentDetector

import logging 
import os
import sys
import json
from utils import makedirs, video_frames_to_grayscale, plot_all_info

logger = logging.getLogger(__name__)

TIME_PER_BAR = 2
SAFE = False

class videoProcessor():
    def __init__(self, video, video_dir) -> None:
        self.video = video
        self.video_dir = video_dir
        self.video_path = os.path.join(self.video_dir, self.video)
        self.flow_dir = 'flow/'
        self.fig_dir = 'fig/'
        self.image_dir = 'image/'
        self.optical_flow_dir = 'optical_flow/'

        optical_flow_file = os.path.join(self.optical_flow_dir, os.path.basename(video).split('.')[0] + '.npz')
        
        if os.path.exists(optical_flow_file):
            # Prompt the user to overwrite existing files or not
            if SAFE:
                overwrite = input("Files already exist. Do you want to overwrite them? (yes/no): ").lower()
                if overwrite != 'yes':
                    sys.exit()  # Exit if the user doesn't want to overwrite

        makedirs([video_dir, self.flow_dir, self.fig_dir, self.image_dir, self.optical_flow_dir])

    def getOpticalFlow(self, method_choice):
        assert os.path.exists(self.video_path)
        
        metadata = skvideo.io.ffprobe(self.video_path)
        self.frame, self.time = metadata['video']['@avg_frame_rate'].split('/')
        self.fps = round(float(self.frame) / float(self.time))
        self.fpb = TIME_PER_BAR * self.fps

        self.video = skvideo.io.vread(self.video_path)[:]
        logging.info("video loaded successfully")
    
        if method_choice == 'lucaskanade_dense':
            self.video_grayscale = video_frames_to_grayscale(self.video)
            method = cv2.optflow.calcOpticalFlowSparseToDense
            flow_magnitude_list = self.denseOpticalFlow(self, method, self.video_grayscale, to_gray=False)
        elif method_choice == 'farneback':
            self.video_grayscale = video_frames_to_grayscale(self.video)
            method = cv2.calcOpticalFlowFarneback
            params = [0.5, 3, 15, 3, 5, 1.2, 0]  # default Farneback's algorithm parameters
            flow_magnitude_list = self.denseOpticalFlow(method, self.video_grayscale, params, to_gray=False)
        elif method_choice == "rlof":
            method = cv2.optflow.calcOpticalFlowDenseRLOF
            flow_magnitude_list = self.denseOpticalFlow(method, self.video)

        self.flow = np.asarray(flow_magnitude_list)
        for percentile in range(10, 101, 10):
            logger.debug('percentile %d: %.4f' % (percentile, np.percentile(self.flow, percentile)))
        
        np.savez(os.path.join(self.flow_dir, os.path.basename(self.video_path).split('.')[0] + '.npz'),
               flow=np.asarray(self.flow))
        
        return
    
    def denseOpticalFlowPerBar(self, flow_magnitude_list):
        flow_magnitude_per_bar = []
        temp = np.zeros((len(flow_magnitude_list)))
        for i in np.arange(0, len(flow_magnitude_list), self.fpb):
            mean_flow = np.mean(flow_magnitude_list[int(i): min(int(i + self.fpb), len(flow_magnitude_list))])
            flow_magnitude_per_bar.append(mean_flow)
            temp[int(i): min(int(i + self.fpb), len(flow_magnitude_list))] = mean_flow
        
        self._flow_per_bar_no_beat = temp
    
        return

    def denseOpticalFlow(self, method, video, params=[], to_gray=False):

        logger.debug("Retrieving Optical Flow ...")
        self.n_frames = len(video) 
        old_frame = video[0]

        flow_magnitude_list = []
        for i in range(1, self.n_frames):
            # Read the next frame
            new_frame = video[i]

            # Calculate Optical Flow
            flow = method(old_frame, new_frame, None, *params)
            flow_magnitude = np.mean(np.abs(flow))
            flow_magnitude_list.append(flow_magnitude)

            # Update the previous frame
            old_frame = new_frame

        self.denseOpticalFlowPerBar(flow_magnitude_list)

        logger.debug("Done Retrieving Optical Flow")
        # return optical_flow, flow_magnitude_list
        return flow_magnitude_list

    def getVideoBeat(self):

        logger.debug("Retrieving Video Beat ...")
        vb.Video.getVisualTempo = vb.Video_CV.getVisualTempo

        video = os.path.basename(self.video_path)
        self.vlog = vb.PullVideo(name=video, source_location=os.path.join(self.video_path), max_height=360)
        vbeats = self.vlog.getVisualBeatSequences(search_window=None)[0]

        self.tempo, self.beats = self.vlog.getVisualTempo()
        logger.debug("Tempo is", self.tempo)
        self.vbeats_list = []

        resolution=1
        for vbeat in vbeats:
            i_beat = round(vbeat.start / 60 * self.tempo * 4)
            vbeat_dict = {
                'start_time': vbeat.start,
                'bar'       : int(i_beat // 16),
                'tick'      : int(i_beat % 16),
                'weight'    : vbeat.weight
            }
            if vbeat_dict['tick'] % resolution == 0:  # only select vbeat that lands on the xth tick
                self.vbeats_list.append(vbeat_dict)
        logger.debug('%d / %d vbeats selected' % (len(self.vbeats_list), len(vbeats)))

        return
    
    def getSceneCuts(self):
        self.scene_list = detect(self.video_path, ContentDetector())

        return
    
    def saveFeatures(self):
        logger.debug("Retrieving Retrieved Features ...")
     
        video = os.path.basename(self.video_path)
        npz = np.load("flow/" + video.replace('.mp4', '.npz'), allow_pickle=True)
        flow_magnitude_list = npz['flow']
        fps = round(self.vlog.n_frames() / float(self.vlog.getDuration()))
        fpb = int(round(fps * 4 * 60 / self.tempo))  # frame per bar

        fmpb = []  # flow magnitude per bar
        temp = np.zeros((len(flow_magnitude_list)))
        for i in range(0, len(flow_magnitude_list), fpb):
            mean_flow = np.mean(flow_magnitude_list[i: min(i + fpb, len(flow_magnitude_list))])
            fmpb.append(float(mean_flow))
            temp[i: min(i + fpb, len(flow_magnitude_list))] = mean_flow
    
        self._flow_per_bar = temp
        #np.savez(os.path.join(self.flow_dir, os.path.basename(self.video_path).split('.')[0] + '_flow_per_bar' + '.npz'),
        #        flow=np.asarray(temp))

        self.metadata = {
            'duration'              : self.vlog.getDuration(),
            'tempo'                 : self.tempo,
            'vbeats'                : self.vbeats_list,
            'flow_magnitude_per_bar': fmpb,
        }    

        with open("metadata.json", "w") as f:
            json.dump(self.metadata, f)

        plot_all_info(self.n_frames, self.flow,self._flow_per_bar, self._flow_per_bar_no_beat, self.scene_list, self.fig_dir)
        np.savez(os.path.join(self.optical_flow_dir, os.path.basename(self.video_path).split('.')[0] + '.npz'),
                                                                                _flow=self.flow, 
                                                                                _flow_per_bar = self._flow_per_bar, 
                                                                                _flow_per_bar_no_beat= self._flow_per_bar_no_beat)
        logger.debug("Done Retrieving Features.")
        
        return