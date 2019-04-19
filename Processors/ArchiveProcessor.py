import os
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class ArchiveProcessor(Processor):

    def __init__(self):
        super().__init__("ARCH")

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        pShot.Shot.filename = pShot.Shot.filenameWithoutExtension + "_cv" + pShot.Shot.filenameExtension
