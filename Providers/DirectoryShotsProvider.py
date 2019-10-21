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
        dtStr = None
        folder = self.folder if self.folder else self.config.path_from
        if len(pShots) > 0 and 'PROV:IMAP' in pShots[0].Metadata and 'start' in pShots[0].Metadata['PROV:IMAP']:
            meta = pShots[0].Metadata
            dtStr = meta['PROV:IMAP']['start']
            dt = self.helper.FromTimeStampStr(dtStr)
            self.log.debug(f'Search files: @{dt} in {folder}')
        else:
            self.log.warning("No event start time found in metadata['PROV:IMAP']")

        # path_from: F:\inetpub\ftproot\Camera\Foscam\FI9805W_C4D6553DECE1
        # to found: \snap\MDAlarm_20190926-122821.jpg
        filenames = list(self.helper.WalkFiles(folder,
                        lambda x: 
                            self.helper.FileNameByDateRange(x, dt, self.config.camera_triggered_interval_sec)
                                and self.helper.IsImage(x),
                        self.config.ignore_dir))

        pShots = [PipelineShot(CamShot(filenames[i]), i) for i in range(len(filenames))]
        for pShot in pShots:
            meta = self.CreateMetadata(pShot)
            meta['start'] = dtStr if dtStr else self.helper.ToTimeStampStr(pShots[0].Shot.GetDatetime())
            meta['filename'] = pShot.OriginalShot.fullname
            yield pShot
