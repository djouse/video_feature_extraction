import os


class SourceMedia:
    def __init__(self, path=None, name=None, **kwargs):
        path_to_test_video = os.path.join("videos")
        self.path = os.path.join("../videos")
        self._name = name
        self.__dict__.update(**kwargs)
    @property
    def name(self):         
        if(self._name is not None):
            return self._name
        else:
            return os.path.splitext(os.path.basename(self.path))[0]
    def getTestVideo(self):
        return os.path.join("../videos", "video.mp4")