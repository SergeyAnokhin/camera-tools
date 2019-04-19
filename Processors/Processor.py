import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig

class Processor:
    config: CameraArchiveConfig

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
        self.log.info('=== PROCESS ===')
        for i in range(len(pShots)):
            pShot = pShots[i]
            otherPShots = pShots.copy()
            otherPShots.remove(pShot)
            self.log.debug(f"====== {pShot.Shot.filename} ========================================")
            self.ProcessShot(pShot, otherPShots)

    def ProcessShot(self, pShot: PipelineShot, otherPShots: []):
        pass