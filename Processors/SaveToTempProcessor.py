import os, cv2
from datetime import datetime  
from datetime import timedelta 
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class SaveToTempProcessor(Processor):
    '''
        Save analysed files to temp \n
        original: temp/20190203_085908_{camera}.jpg \n
        analysed: temp/20190203_085908_{camera}_cv.(jpeg|png) \n
    '''
    def __init__(self, isSimulation: bool = False):
        super().__init__("TEMP")
        self.isSimulation = isSimulation
    
    def ProcessItem(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)

        dt = pShot.Shot.GetDatetime()
        camera = self.config.camera

        fullname = os.path.join('temp', f'{dt:%Y%m%d_%H%M%S}_{camera}_cv.jpeg')
        fullname_orig = os.path.join('temp', f'{dt:%Y%m%d_%H%M%S}_{camera}.jpg')
        self.log.info(f'    - CV   save: {fullname}')
        self.log.info(f'    - ORIG save: {fullname_orig}')

        pShot.Shot.Save(fullname)
        if self.isSimulation:
            pShot.OriginalShot.Save(fullname_orig)
        else:
            pShot.OriginalShot.Move2(fullname_orig)

        meta['fullname'] = pShot.Shot.fullname
        meta['original_fullname'] = pShot.OriginalShot.fullname
