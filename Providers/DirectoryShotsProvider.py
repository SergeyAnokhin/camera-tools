import os, logging
from datetime import datetime
from Pipeline.Model.CamShot import CamShot
from Providers.Provider import Provider

class DirectoryShotsProvider(Provider):
    Shots = []

    def __init__(self):
        super().__init__("DIR")

    def FromDir(self, folder: str):
        self = DirectoryShotsProvider()
        self.Shots = [CamShot(os.path.join(folder, f)) for f in os.listdir(folder)]   
        self.log.debug("Loaded {} shots from directory {}".format(len(self.Shots), folder)) 
        return self

    def GetShots(self, dt: datetime = datetime.now):
        for s in self.Shots:
            s.LoadImage()
        return self.Shots