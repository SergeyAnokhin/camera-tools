import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig

class Provider:
    config: CameraArchiveConfig
    isSimulation: bool

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(f"PROV:{name}")

    def CreateMetadata(self, pShot: PipelineShot):
        pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def GetShots(self, pShots: []):
        return pShots
