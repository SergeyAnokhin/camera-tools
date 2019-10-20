import logging
from Pipeline.Model.PipelineShot import PipelineShot
from Pipeline.Model.CamShot import CamShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig

class Provider:
    config: CameraArchiveConfig
    isSimulation: bool

    def __init__(self, name):
        self.name = f'PROV:{name}'
        self.log = logging.getLogger(f"PROV:{name}")

    def CreateMetadata(self, pShot: PipelineShot):
        pShot.Metadata[self.name] = {}
        return pShot.Metadata[self.name]

    def GetShots(self, pShots: []):
        self.log.info(f'<<<<<< SHOTS: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')
        newPShots = self.GetShotsProtected(pShots)
        newPShots = filter(lambda s: not self.AlreadyHasShotAtThisTime(pShots, s), newPShots)
        # newPShots.filt [s for s in newPShots if not self.AlreadyHasShotAtThisTime(pShots, s)]
        pShots += newPShots
        pShots.sort(key = lambda s: s.Shot.GetDatetime())
        for i,s in enumerate(pShots):
            s.Index = i
            self.log.debug(f'   <<< #{s.Index} {s.Shot.filename} @{s.Shot.GetDatetime():%H:%M:%S} (full: {s.Shot.fullname})')

        return pShots

    def AlreadyHasShotAtThisTime(self, pShots: [], newShot: PipelineShot):
        return any(s.Shot.GetDatetime() == newShot.Shot.GetDatetime() for s in pShots)

    def GetShotsProtected(self, pShots: []):
        return pShots #abstract method