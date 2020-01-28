import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Common.CommonHelper import CommonHelper

class Processor:
    config: CameraArchiveConfig
    isSimulation: bool = False

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(f"PROC:{name}")
        self.helper = CommonHelper()

    def Preload(self, isUsed = False):
        ''' Will start on application start once '''
        if isUsed:
            self.log.info('=== PRELOAD ===')

    def Process(self, pShots: [], pipelineContext: dict):
        ''' Main Process '''
        self.log.info(f'@@@ ⏳ PROCESS: ***{self.name}*** @@@@@@@@@@@@@@@@@@@@@@@@ {"(Simulation)" if self.isSimulation else ""}')
        for i in range(len(pShots)):
            pShot = pShots[i]
            self.log.debug(f"   === 🎞️  {pShot.Shot.filename} ======")
            self.ProcessShot(pShot, pShots)
        self.AfterProcess(pShots, pipelineContext)

    def CreateMetadata(self, pShot: PipelineShot):
        pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def ProcessShot(self, pShot: PipelineShot, otherPShots: []):
        pass

    def AfterProcess(self, pShots: [], ctx):
        pass

    def PostProcess(self, pShots: []):
        pass