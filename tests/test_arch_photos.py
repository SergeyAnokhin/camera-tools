import logging, unittest, os, filetype
from datetime import datetime
from pprint import pprint
import PIL.ExifTags # pip install pillow
import enzyme
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import hachoir
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.test")
from Common.CommonHelper import CommonHelper
from Pipeline.Pipeline import Pipeline
from tests.TestHelper import TestHelper

class TestArchPhotos(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestArchPhotos, self).__init__(*args, **kwargs)
        self.testHelper = TestHelper()
        self.helper = CommonHelper()
        self.log = self.testHelper.CreateLog(TestArchPhotos.__name__)

    def setUp(self):
        self.testHelper.setUp(self.log, self._testMethodName)

    def tearDown(self):
        self.testHelper.tearDown(self.log, self._testMethodName)

    def test_DateTimeParsing(self):
        # python -m unittest tests.test_arch_photos.TestArchPhotos.test_DateTimeParsing
        files = self.helper.WalkFiles("../camera-OpenCV-data/Mobile", lambda f: True, ['Lilia'])
        for f in files:
            info = MediaInfo(f)
            print(info)

    # def test_CopySimulation(self):
    #     # python -m unittest tests.test_arch_photos.TestArchPhotos.test_CopySimulation
    #     self.assertTrue(False)

class MediaInfo:

    def __init__(self, filename = None):
        if not filename:
            return
        self.helper = CommonHelper()
        print(f'========== {filename} ==========')
        self.filename = filename
        self.datetime_name = self.helper.get_datetime(self.filename, False)
        # if dt != None:
        #     self.log.debug(f"{dt:%Y-%m-%d %H:%M:%S} File: {f}")

        kind = filetype.guess(self.filename)
        if kind is None:
            print(f'Cannot guess file type: {self.filename}')
        else:
            self.mediatype = kind.mime.split('/')[0]
            self.mediaextension = kind.mime.split('/')[1]

        if self.mediatype == 'image':
            imgFile = PIL.Image.open(self.filename)
            try:
                exifDict = imgFile._getexif()
            except AttributeError as err:
                print(f'Error during extract exif: {err}')
                exifDict = None            
            if exifDict:
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in exifDict.items()
                    if k in PIL.ExifTags.TAGS
                }
                # pprint(self.filename)
                # pprint(exif['DateTimeDigitized'])
                self.datetime_meta_create = self.helper.get_datetime(exif['DateTimeDigitized'])
            else:
                print(f"No exif data in {self.filename}")
        elif self.mediatype == 'video':
            # with open(self.filename, 'rb') as f:
            #     mkv = enzyme.VideoTrack()
            # pprint(mkv.info)
            parser = createParser(self.filename)
            if not parser:
                print(f"Can't parse file: {self.filename}")
            
            with parser:
                try:
                    metadata = extractMetadata(parser)
                except Exception as err:
                    print("Metadata extraction error: %s" % err)
                    metadata = None
            if not metadata:
                print("Unable to extract metadata")
            else:
                dic = metadata.exportDictionary()
                pprint(dic)
                self.datetime_meta_create = self.helper.get_datetime(dic['Metadata']['Creation date'])

        stat = os.stat(self.filename)
        self.datetime_file_create = datetime.fromtimestamp(stat.st_ctime)
        self.datetime_file_modif = datetime.fromtimestamp(stat.st_mtime)
        
        # # img = PIL.Image.open(f)
        # # exif_data = img._getexif()
        # print(exif)
    def __str__(self):
        props = ['datetime_meta_create', 'datetime_name', 'datetime_file_create', 'datetime_file_modif']
        dic = MediaInfo()
        for k in props:
            if k not in self.__dict__:
                continue
            v = self.__dict__[k]
            if not v:
                continue
            dtStr = self.helper.ToTimeStampStr(v)
            dic.__setattr__(k, dtStr)

        return str(vars(dic))


