from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Archiver.CameraArchiveHelper import CameraArchiveHelper
from Pipeline.Model.PipelineShot import PipelineShot
# using cases :
# 1. New mail comes
# 2. Re-index whole archive
# 3. (?) Process video

class ShotsPipeline:

    def __init__(self, camera: str):
        self.processors = []
        self.archiver = CameraArchiveHelper()
        self.config = self.archiver.load_configs("configs", [ camera ])[0]

    def PreLoad(self):
        for processor in self.processors:
            processor.config = self.config
            PreLoad = getattr(processor, "PreLoad", None)
            if callable(PreLoad):
                processor.PreLoad()

    def Process(self, shots: []):
        pShots = [PipelineShot(shots[i], i) for i in range(len(shots))]
        for processor in self.processors:
            processor.Process(pShots)
            PostProcess = getattr(processor, "PostProcess", None)
            if callable(PostProcess):
                processor.PostProcess(pShots)

        return pShots

    def Show(self):
        pass
