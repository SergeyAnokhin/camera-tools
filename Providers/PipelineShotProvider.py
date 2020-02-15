import logging
from asq import query
from Pipeline.Model.PipelineShot import PipelineShot
from Pipeline.Model.CamShot import CamShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Providers.Provider import Provider

class PipelineShotProvider(Provider):
    config: CameraArchiveConfig

    def __init__(self, name, isSimulation: bool):
        super().__init__(name, isSimulation)

    def CreateMetadata(self, pShot: PipelineShot):
        pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def GetShots(self, pShots: []):
        self.log.info(f'<<<<<< SHOTS: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')
        newPShots = list(self.GetShotsProtected(pShots))
        for i,s in enumerate(newPShots):
            self.log.debug(f'   <+++ #{s.Index} {s.Shot.filename} @{s.Shot.GetDatetime():%H:%M:%S} (full: {s.Shot.fullname})')
    
        pShots = query(pShots).union(newPShots, self.GetTime).to_list()
        # newPShots = filter(lambda s: not self.AlreadyHasShotAtThisTime(pShots, s), newPShots)
        # # newPShots.filt [s for s in newPShots if not self.AlreadyHasShotAtThisTime(pShots, s)]
        # pShots += newPShots
        # pShots.sort(key = lambda s: s.Shot.GetDatetime())
        for i,s in enumerate(pShots):
            s.Index = i

        return pShots

    def GetTime(self, pShot1: PipelineShot):
        return pShot1.Shot.GetDatetime() 

    def AlreadyHasShotAtThisTime(self, pShots: [], newShot: PipelineShot):
        return any(s.Shot.GetDatetime() == newShot.Shot.GetDatetime() for s in pShots)

    def GetShotsProtected(self, pShots: []):
        return pShots #abstract method