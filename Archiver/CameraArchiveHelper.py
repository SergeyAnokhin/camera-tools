import json, os, shutil, logging
from Archiver.FileArchive import FileArchive
from Common.ElasticSearchHelper import ElasticSearchHelper
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Common.CommonHelper import CommonHelper

class CameraArchiveHelper:

    def __init__(self, isSimulation: bool = False):
        self.log = logging.getLogger(f"CAHE")
        self.isSimulation = isSimulation

    def load_configs(self, dir, listConfig = []):
        configs = []
        for file in os.listdir(dir):
            if not file.startswith('camera-'):
                continue 
            config = CameraArchiveConfig()
            config.fromJsonFile(os.path.join(dir, file))    
            if len(listConfig) == 0 or config.camera in listConfig:
                self.log.info('Load Config: {} => {}'.format(file, config.camera))
                configs.append(config)
        return configs

    def get_files(self, config):
        files = []
        for root, dirnames, filenames in os.walk(config.pathFrom()):
            if hasattr(config, 'ignore_dir') and self.dir_to_ignore(root, config.ignore_dir):
                self.log.info('Ignore:', root)
                continue
            for filename in filenames: #fnmatch.filter(filenames, '*.c'):
                try:
                    file = FileArchive(config, root, filename)
                    files.append(file)
                except ValueError:
                    self.log.info('FileArchive creation error')
        self.log.info(f'{len(files)} files found in {config.pathFrom()}')
        return files

    def dir_to_ignore(self, root: str, ignore_dir: []):
        for dir in ignore_dir:
            if dir in root:
                return True
        return False

    def move_files(self, files, config):
        common = CommonHelper()
        elastic = ElasticSearchHelper()
        exts = {}

        last_file_dir_relative_to = ''
        bytes_moved = 0
        files_moved = 0
        for file in files:
            dir_relative_to = file.to.get_dir_relative(config.path_to)
            dir_relative_frm = file.frm.get_dir_relative(config.pathFrom())
            if last_file_dir_relative_to != dir_relative_to:
                if last_file_dir_relative_to != '':
                    ext_stat = ' '.join(["{}:{}".format(k.upper(), exts[k]) for k in exts])
                    self.log.info('\t{} files moved: {}. Total {}'.format(files_moved, ext_stat, common.size_human(bytes_moved)))
                    files_moved = 0
                    bytes_moved = 0
                    exts = {}
                self.log.info('{} => {}'.format(dir_relative_frm, dir_relative_to))

            files_moved += 1
            bytes_moved += file.frm.size()
            #print('\t - {} ({})'.format(file.frm.filename, file.frm.size_human()))
            # print(os.path.dirname(file.path_to))
            #pprint(file.__dict__)
            os.makedirs(file.to.dir, exist_ok=True)
            ## os.rename("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            ##shutil.copy2(file.frm.path, file.to.path)
            if self.isSimulation:
                self.log.info(f'{file.frm.path} => {file.to.path}')
            else:
                shutil.move(file.frm.path, file.to.path)
                elastic.report_to_elastic(file)

            ext = file.to.get_extension()
            if ext not in exts:
                exts[ext] = 0
            exts[ext] += 1

            last_file_dir_relative_to = dir_relative_to
            #break

        ext_stat = ' '.join(["{}:{}".format(k.upper(), exts[k]) for k in exts])
        self.log.info('\t{} files moved: {}. Total {}'.format(files_moved, ext_stat, common.size_human(bytes_moved)))
        files_moved = 0
        bytes_moved = 0
        self.log.info('########################################################')
