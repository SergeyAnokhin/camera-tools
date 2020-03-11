import os
from Common.AppSettings import AppSettings
from Common.CommonHelper import CommonHelper
from Processors.Processor import Processor

class PhotosArrangeProcessor(Processor):

    def __init__(self, label: str, isSimulation: bool = False):
        super().__init__("PHOT", isSimulation)
        self.label = label
        self.helper = CommonHelper()

    def ProcessItem(self, filename: str, context: dict):
        # self.log.debug(f'   From: {filename}')
        basename = os.path.basename(filename)
        dt = context['meta']['CRED'][filename]['shottime']
        dtPath = dt.strftime('%Y/%y-%m') + ' ' + self.label
        toPath = os.path.join(AppSettings.PHOTO_ARCHIVE_PATH, dtPath)
        to = os.path.join(toPath, basename)
        # self.log.debug(f'   To:   {to}')
        meta = self.CreateMetadata(filename, context)
        meta['arch_path'] = to

        self.helper.EnsureMove(filename, to, 'copy' if self.isSimulation else 'move')
        