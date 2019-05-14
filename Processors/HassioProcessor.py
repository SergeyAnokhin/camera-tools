import os, shutil
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class HassioProcessor(Processor):
    '''
        update files in hassio server
    '''
    def __init__(self):
        super().__init__("HASS")
        self.hassLocation = "\\\\192.168.1.36\\config\\www\\snapshot"

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)
        camera = self.config.camera
        dest = os.path.join(self.hassLocation, f'cv_{camera}.jpg')
        meta['hassio_location'] = dest
        shutil.copy2(pShot.Shot.fullname, dest)