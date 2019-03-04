import os
import re
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Common.FileInfo import FileInfo


class FileArchive:
    frm: FileInfo
    to: FileInfo

    def __init__(self, config: CameraArchiveConfig, root = '', filename = ''):
        self.config = config
        if not root and not filename:
            return

        full_filename = os.path.join(root, filename)
        self.frm = FileInfo(full_filename)

        full_filename = self.get_full_filename_to()
        self.to = FileInfo(full_filename)

    def force_values(self, to: FileInfo, frm: FileInfo):
        self.frm = frm
        self.to = to

    def get_full_filename_to(self):
        dt = self.frm.get_datetime()
        pattern = dt.strftime('%Y.*%m.*%d')
        # add date if need
        # if re.search(pattern, self.frm.dir_relative):
        #     return os.path.join(self.config.path_to, self.frm.path_relative.strip('\\'))
        # return os.path.join(self.config.path_to, dt.strftime('%Y-%m\\%d'), self.frm.path_relative.strip('\\'))
        #os.path.basename(self.frm.path_relative)
        return os.path.join(self.config.path_to, dt.strftime('%Y-%m\\%d'), self.frm.filename)

    def __repr__(self):
        return '{}: \n\t <= {}\n\t => {}'.format(self.frm.dir_relative,  self.frm.path, self.to.path)


