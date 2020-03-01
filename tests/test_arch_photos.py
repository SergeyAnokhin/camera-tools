import logging, unittest, os
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.test")
from Common.CommonHelper import CommonHelper
from Common.MediaInfo import MediaInfo
from tests.TestHelper import TestHelper

from Pipeline.Pipeline import Pipeline
from Providers.FilesWalkerProvider import FilesWalkerProvider

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
        pipeline = Pipeline()
        pipeline.providers.append(FilesWalkerProvider("../camera-OpenCV-data/Mobile", ['Lilia']))

        # files = self.helper.WalkFiles("../camera-OpenCV-data/Mobile", lambda f: True, ['Lilia'])

        # for f in files:
        #     info = MediaInfo(f)
        #     self.log.debug(info)

    # def test_CopySimulation(self):
    #     # python -m unittest tests.test_arch_photos.TestArchPhotos.test_CopySimulation
    #     self.assertTrue(False)


