from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class ArchiveProcessor(Processor):
    
    def __init__(self):
        super().__init__("ARCH")

    def ProcessShot(self, pShot: PipelineShot, others: []):
        pass
