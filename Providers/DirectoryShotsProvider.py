import os, logging
from datetime import datetime
from Pipeline.Model.CamShot import CamShot

class DirectoryShotsProvider:
    Shots = []

    def __init__(self):
        self.log = logging.getLogger("PROV:DIR")

    def FromDir(self, folder: str):
        self = DirectoryShotsProvider()
        self.Shots = [CamShot(os.path.join(folder, f)) for f in os.listdir(folder)]   
        self.log.debug("Loaded {} shots from directory {}".format(len(self.Shots), folder)) 
        return self

    def GetShots(self, dateTime):
        return self.Shots