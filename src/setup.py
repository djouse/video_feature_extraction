import argparse
import logging
import os
import subprocess

def setup(debug_mode):
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] :: %(message)s", "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    if debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Application in DEBUG Mode")
    else:
        logging.getLogger().setLevel(logging.INFO)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(args.log_dir, "log"), mode='w')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
        logging.info("Application in INFO Mode")

    if not os.path.exists(args.video_360p_dir):    
        os.makedirs(args.video_360p_dir)
        result = subprocess.call(["ffmpeg", "-i", os.path.join(args.video_dir ,args.video), 
                                            "-strict", "-2",
                                            "-vf", "scale=-1:360",
                                            os.path.join(args.video_360p_dir, "video.mp4"),
                                            "-y"])
        return

parser = argparse.ArgumentParser(description='Motion analysis and beat-timing video mapping features.')

parser.add_argument('--debug', default=False, type=bool,
                    help="Debug session set to True does not create log file for experiment and all info is displayed on console")

parser.add_argument('--video', default="video.mp4", type=str)
parser.add_argument('--video_dir', default="../videos", type=str)
parser.add_argument('--video_360p_dir', default="../videos/360p_input/", type=str)
parser.add_argument('--log_dir', default="../log", type=str)

parser.add_argument('--gui', default=False, type=bool) #TODO

parser.add_argument("--optical_flow_method", choices=["farneback", "lucaskanade_dense", "rlof"], default="farneback")

args = parser.parse_args()

#check if video and path exists TODO
#check if input args are all valid and if they need debugging TODO
setup(args.debug)
