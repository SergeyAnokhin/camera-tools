import os, shutil
from Processors.PipelineShotProcessor import PipelineShotProcessor
from Pipeline.Model.PipelineShot import PipelineShot
from Common.AppSettings import AppSettings

class HassioProcessor(PipelineShotProcessor):
    '''
        update files in hassio server
    '''
    def __init__(self, overidePath = None):
        super().__init__("HASS")
        self.hassLocation = AppSettings.HASSIO_PATH
        if overidePath != None:
            self.hassLocation = overidePath

    def ProcessItem(self, pShot: PipelineShot, pShots: []):
        if not self.hassLocation:
            self.log.warn(f'Copy to hassio ignored. HASSIO_PATH not defined in config.')
            return
        meta = self.CreateMetadata(pShot)
        camera = self.config.camera
        dest = os.path.join(self.hassLocation, f'cv_{camera}_{pShot.Index}.jpg')
        meta['hassio_location'] = dest
        self.log.info(f'- Copy: {dest}')
        shutil.copy2(pShot.Shot.fullname, dest)