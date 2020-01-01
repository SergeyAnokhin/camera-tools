import os
from Processors.Processor import Processor
from Common.SecretConfig import SecretConfig
from Pipeline.Model.PipelineShot import PipelineShot

class ArchiveProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("ARCH")
        self.isSimulation = isSimulation

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)
        dt = pShot.Shot.GetDatetime()

        path = os.path.join(self.config.pathTo(), dt.strftime('%Y-%m'),
            dt.strftime('%d'))
        filename_date = dt.strftime('%Y%m%d_%H%M%S')
        filename = f'{filename_date}_{self.config.camera}_cv.jpeg'
        filename_orig = f'{filename_date}_{self.config.camera}.jpg'

        dest = os.path.join(path, filename)
        dest_orig = os.path.join(path, filename_orig)

        # pShot.Shot.filename = pShot.Shot.filenameWithoutExtension + "_cv" + pShot.Shot.filenameExtension
        self.log.info(f'    - CV   Move: {dest}')
        self.log.info(f'    - ORIG Move: {dest_orig}')
        dest_path = os.path.dirname(dest)
        meta['archive_destination'] = dest
        meta['archive_destination_orig'] = dest_orig
        if not self.isSimulation:
            if not os.path.exists(dest_path):
                self.log.debug(f'- create archive directory: {dest_path}')
                os.makedirs(dest_path, exist_ok=True)
            pShot.Shot.Move2(dest)
            pShot.OriginalShot.Move2(dest_orig)
        else:
            if not os.path.exists(dest_path):
                self.log.debug(f'- create archive directory (Simulation): {dest_path}')
