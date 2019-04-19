import os
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class SaveToTempProcessor(Processor):
    '''
        Save analysed files to temp \n
        original: temp/20190203-085908-{camera}-{n}.jpg \n
        analysed: temp/20190203-085908-{camera}-{n}.(jpeg|png) \n
    '''
    def __init__(self):
        super().__init__("ARCH")
    
    def ProcessShot(self, pShot: PipelineShot, others: []):
        pShot.fullname = os.path.join('temp', pShot.filename)
