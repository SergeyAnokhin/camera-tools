import os, logging, datetime
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.PipelineShot import PipelineShot
from Providers.Provider import Provider
from Common.CommonHelper import CommonHelper

class DirectoryShotsProvider(Provider):

    def __init__(self):
        super().__init__("DIR")
        self.helper = CommonHelper()

    def FromDir(self, folder: str):
        self = DirectoryShotsProvider()
        shots = [CamShot(os.path.join(folder, f)) for f in os.listdir(folder)]   
        self.log.debug("Loaded {} shots from directory {}".format(len(shots), folder)) 
        for s in shots:
            s.LoadImage()
        return shots

    def GetShots(self, pShots: []):
        if len(pShots) == 0 or 'IMAP' not in pShots[0].Metadata or 'datetime' not in pShots[0].Metadata['IMAP']:
            return pShots

        meta = pShots[0].Metadata
        dtStr = meta['IMAP']['datetime']
        dt = datetime.datetime.strptime(dtStr, '%Y-%m-%d %H:%M:%S')
        self.log.debug(f'Base datetime for search files: {dt}')
        # path_from: F:\inetpub\ftproot\Camera\Foscam\FI9805W_C4D6553DECE1
        # to found: \snap\MDAlarm_20190926-122821.jpg
        filenames = self.helper.WalkFiles(self.config.path_from,
                        lambda x: self.FileNameByDateRange(x, dt, datetime.timedelta(seconds=15)),
                        self.config.ignore_dir)
        shots = [CamShot(f) for f in filenames]
        [s.LoadImage() for s in shots]
        filesList = ", ".join(map(lambda f: f.fullname, shots))
        self.log.debug(f'Found shots: {len(shots)}: {filesList}')
        newPShots = [PipelineShot(s) for s in shots if not self.AlreadyHasShotAtThisTime(pShots, s)]
        pShots += newPShots
        pShots.sort(key = lambda s: s.Shot.GetDatetime())
        for i,s in enumerate(pShots):
            s.Index = i
            self.log.debug(f'#{s.Index} {s.Shot.fullname} @{s.Shot.GetDatetime():%H:%M:%S}')

        return pShots

    def AlreadyHasShotAtThisTime(self, pShots: [], newShot: CamShot):
        return any(s.Shot.GetDatetime() == newShot.GetDatetime() for s in pShots)

    def FileNameByDateRange(self, filename: str, start: datetime, delta: datetime.timedelta):
        dtFile = self.helper.get_datetime(filename)
        dtMax = start + delta
        return start <= dtFile <=dtMax
