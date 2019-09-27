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

        path = os.path.join(self.config.path_to, dt.strftime('%Y-%m'), dt.strftime('%d'))
        filename_date = dt.strftime('%Y%m%d_%H%M%S')
        filename = f'{filename_date}_{self.config.camera}_cv.jpeg'
        filename_orig = f'{filename_date}_{self.config.camera}.jpg'

        dest = os.path.join(path, filename)
        dest_orig = os.path.join(path, filename_orig)

        meta['archive_destination'] = dest
        meta['archive_destination_orig'] = dest_orig
        # pShot.Shot.filename = pShot.Shot.filenameWithoutExtension + "_cv" + pShot.Shot.filenameExtension
        if not self.isSimulation:
            pShot.Shot.Move(dest)
            pShot.OriginalShot.Move(dest_orig)
