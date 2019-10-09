import os, logging, datetime
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.PipelineShot import PipelineShot
from Providers.Provider import Provider
from Common.CommonHelper import CommonHelper

class DirectoryShotsProvider(Provider):

    def __init__(self, folder: str = None):
        super().__init__("DIRC")
        self.helper = CommonHelper()
        self.folder = folder

    def FromDir(self, folder: str):
        self = DirectoryShotsProvider()
        shots = [CamShot(os.path.join(folder, f)) for f in os.listdir(folder)]   
        self.log.debug("Loaded {} shots from directory {}".format(len(shots), folder)) 
        for s in shots:
            s.LoadImage()
        return [PipelineShot(s, i) for i, s in enumerate(shots)]

    def GetShotsProtected(self, pShots: []):
        dt: datetime = None
        folder = self.folder if self.folder else self.config.path_from
        if len(pShots) > 0 and 'IMAP' in pShots[0].Metadata and 'datetime' in pShots[0].Metadata['IMAP']:
            meta = pShots[0].Metadata
            dtStr = meta['IMAP']['datetime']
            dt = datetime.datetime.strptime(dtStr, '%Y-%m-%d %H:%M:%S')
            self.log.debug(f'Base datetime for search files: {dt}')

        # path_from: F:\inetpub\ftproot\Camera\Foscam\FI9805W_C4D6553DECE1
        # to found: \snap\MDAlarm_20190926-122821.jpg
        filenames = self.helper.WalkFiles(folder,
                        lambda x: self.helper.FileNameByDateRange(x, dt, self.config.camera_triggered_interval_sec),
                        self.config.ignore_dir)
        return [PipelineShot(CamShot(f)) for f in filenames]
        #[s.LoadImage() for s in shots]
        # filesList = ", ".join(map(lambda f: f.filename, shots))
        # self.log.debug(f'Found shots: {len(shots)}: {filesList}')
        #return [PipelineShot(s) for s in shots]
