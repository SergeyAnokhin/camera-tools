import os
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class ArchiveProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("ARCH")
        self.isSimulation = isSimulation

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)
        dt = pShot.Shot.GetDatetime()
        dest = os.path.join(self.config.path_to, dt.strftime('%Y-%m'), dt.strftime('%d'), dt.strftime('%Y%m%d_%H%M%S_cv.jpeg'))
        dest_orig = os.path.join(self.config.path_to, dt.strftime('%Y-%m'), dt.strftime('%d'), dt.strftime('%Y%m%d_%H%M%S.jpg'))
        meta['archive_destination'] = dest
        meta['archive_destination_orig'] = dest_orig
        # pShot.Shot.filename = pShot.Shot.filenameWithoutExtension + "_cv" + pShot.Shot.filenameExtension
        if not self.isSimulation:
            pass
            # Copy origin 
            # Copy analysed (_cv)
