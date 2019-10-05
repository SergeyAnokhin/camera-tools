import os, logging
from datetime import datetime
from Pipeline.Model.CamShot import CamShot
from Providers.Provider import Provider

class DirectoryShotsProvider(Provider):

    def __init__(self):
        super().__init__("DIR")

    def FromDir(self, folder: str):
        self = DirectoryShotsProvider()
        shots = [CamShot(os.path.join(folder, f)) for f in os.listdir(folder)]   
        self.log.debug("Loaded {} shots from directory {}".format(len(shots), folder)) 
        for s in shots:
            s.LoadImage()
        return shots

    def GetShots(self, pShots: []):
        if len(pShots) > 0:
            meta = pShots[0].Metadata
            if 'IMAP' in meta:
                if 'datetime' in meta['IMAP']:
                    dtStr = meta['IMAP']['datetime']
                    dt = datetime.strptime(dtStr, '%Y-%m-%d %H:%M:%S')
                    self.log.debug(f'Base datetime for search files: {dt}')
                    # path_from: F:\inetpub\ftproot\Camera\Foscam\FI9805W_C4D6553DECE1
                    # to found: \snap\MDAlarm_20190926-122821.jpg
                    pathSearch = self.config.path_from

        return pShots

