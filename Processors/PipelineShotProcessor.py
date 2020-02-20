import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Common.CommonHelper import CommonHelper
from Processors.Processor import Processor

class PipelineShotProcessor(Processor):
    config: CameraArchiveConfig

    def __init__(self, name, isSimulation=False):
        super().__init__(name, isSimulation)
        self.helper = CommonHelper()

    def CreateMetadata(self, pShot: PipelineShot):
        if self.name not in pShot.Metadata:
            pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def BeforeProcessItem(self, pShot, ctx):
        self.log.debug(f"   === 🎞️  {pShot.Shot.filename} ======")

