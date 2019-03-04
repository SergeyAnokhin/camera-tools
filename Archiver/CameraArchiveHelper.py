import json
import os
import shutil
from elasticsearch import Elasticsearch
from Archiver.FileArchive import FileArchive
from Common.ElasticSearchHelper import ElasticSearchHelper
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Common.CommonHelper import CommonHelper


class CameraArchiveHelper:

    def load_configs(self, dir, listConfig = []):
        configs = []
        for file in os.listdir(dir):
            if not file.startswith('camera-'):
                continue 
            config = CameraArchiveConfig()
            config.fromJsonFile(os.path.join(dir, file))    
            if len(listConfig) == 0 or config.camera in listConfig:
                print('Load Config: {} => {}'.format(file, config.camera))
                configs.append(config)
        return configs

    def get_files(self, config):
        files = []
        for root, dirnames, filenames in os.walk(config.path_from):
            if self.dir_to_ignore(root, config.ignore_dir):
                print('Ignore:', root)
                continue
            for filename in filenames: #fnmatch.filter(filenames, '*.c'):
                try:
                    file = FileArchive(config, root, filename)
                    files.append(file)
                except ValueError:
                    print('FileArchive creation error')
        print('{} files found'.format(len(files)))
        return files

    def dir_to_ignore(self, root: str, ignore_dir: []):
        for dir in ignore_dir:
            if dir in root:
                return True
        return False

    def move_files(self, files):
        common = CommonHelper()
        elastic = ElasticSearchHelper()

        last_file_dir_relative_to = ''
        bytes_moved = 0
        files_moved = 0
        for file in files:
            if last_file_dir_relative_to != file.to.dir_relative:
                if last_file_dir_relative_to != '':
                    print('{} files moved. Total {}'.format(files_moved, common.size_human(bytes_moved)))
                    files_moved = 0
                    bytes_moved = 0
                print('{} => {}'.format(file.frm.dir_relative, file.to.dir_relative))

            files_moved += 1
            bytes_moved += file.frm.size()
            #print('\t - {} ({})'.format(file.frm.filename, file.frm.size_human()))
            # print(os.path.dirname(file.path_to))
            #pprint(file.__dict__)
            os.makedirs(file.to.dir, exist_ok=True)
            ## os.rename("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            ##shutil.copy2(file.frm.path, file.to.path)
            #print(file.frm.path, ' => ', file.to.path)
            shutil.move(file.frm.path, file.to.path)
            elastic.report_to_elastic(file)

            last_file_dir_relative_to = file.to.dir_relative
            #break

        print('{} files moved. Total {}'.format(files_moved, common.size_human(bytes_moved)))
        files_moved = 0
        bytes_moved = 0
        print ('########################################################')
