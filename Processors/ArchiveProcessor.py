import os
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Archiver.CameraArchiveHelper import CameraArchiveHelper
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class ArchiveProcessor(Processor):
    
    def __init__(self):
        super().__init__("ARCH")
        self.archiver = CameraArchiveHelper()

    def PreLoad(self):
        self.config = self.archiver.load_configs("configs", [ self.camera ])

    def ProcessShot(self, pShot: PipelineShot, others: []):
        pShot.Shot.filename = pShot.Shot.filenameWithoutExtension + "_cv" + pShot.Shot.filenameExtension
