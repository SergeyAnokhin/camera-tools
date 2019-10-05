import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig

class Processor:
    config: CameraArchiveConfig
    isSimulation: bool

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(f"PROC:{name}")
        self.PipelineResults = {}

    def Preload(self, isUsed = False):
        ''' Will start on application start once '''
        if isUsed:
            self.log.info('=== PRELOAD ===')

    def Process(self, pShots: []):
        ''' Main Process '''
        self.log.info(f'@@@ PROCESS: ***{self.name}*** @@@@@@@@@@@@@@@@@@@@@@@@')
        for i in range(len(pShots)):
            pShot = pShots[i]
            self.log.debug(f"====== {pShot.Shot.filename} ======")
            self.ProcessShot(pShot, pShots)

    def CreateMetadata(self, pShot: PipelineShot):
        pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def ProcessShot(self, pShot: PipelineShot, otherPShots: []):
        pass

    def PostProcess(self, pShots: []):
        pass