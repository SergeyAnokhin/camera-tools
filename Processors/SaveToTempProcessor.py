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
    def __init__(self):
        super().__init__("TEMP")
    
    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)

        dt = pShot.Shot.GetDatetime()
        index = pShot.Shot.GetMailAttachmentIndex()
        dt = dt + timedelta(seconds=index)
        camera = self.config.camera

        fullname = os.path.join('temp', f'{dt:%Y%m%d_%H%M%S}_{camera}_cv.jpeg')
        pShot.Shot.UpdateFullName(fullname)
        meta['fullname'] = pShot.Shot.fullname

        fullname = os.path.join('temp', f'{dt:%Y%m%d_%H%M%S}_{camera}.jpg')
        pShot.OriginalShot.UpdateFullName(fullname)
        meta['original_fullname'] = pShot.OriginalShot.fullname

        pShot.Shot.Save()
        pShot.OriginalShot.Save()
