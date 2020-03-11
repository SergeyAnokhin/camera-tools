import logging, unittest, os, datetime
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.test")
from Common.CommonHelper import CommonHelper
from Common.MediaInfo import MediaInfo
from tests.TestHelper import TestHelper

from Pipeline.Pipeline import Pipeline
from Providers.FilesWalkerProvider import FilesWalkerProvider
from Processors.MediaCreationDateProcessor import MediaCreationDateProcessor
from Processors.PhotosArrangeProcessor import PhotosArrangeProcessor

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
        pipeline.processors.append(MediaCreationDateProcessor())

        ctx = {}
        pipeline.Get(ctx)
        pipeline.Process(ctx)

        files = ctx['items']
        self.assertEqual(17, len(files))
        # for key in ctx['meta']['CRED']:
        #     dt = ctx["meta"]["CRED"][key]["shottime"]
        #     print(f'self.assertMeta(ctx, "CRED", "{key}", "shottime", datetime.datetime({dt:%Y,%m,%d,%H,%M,%S})')

        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200119_210817.jpg", "shottime", datetime.datetime(2020,1,19,21,8,17))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200119_210851.jpg", "shottime", datetime.datetime(2020,1,19,21,8,51))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200119_210858.mp4", "shottime", datetime.datetime(2020,1,19,20,9,39))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200120_121128.jpg", "shottime", datetime.datetime(2020,1,19,21,8,51))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200120_121259.jpg", "shottime", datetime.datetime(2020,1,19,21,8,17))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200223_095605_1.jpg", "shottime", datetime.datetime(2020,2,23,9,56,5))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\20200223_194631(0).jpg", "shottime", datetime.datetime(2020,2,23,19,46,31))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\FACE_SC_1559419370165.jpg", "shottime", datetime.datetime(2019,6,1,22,2,54))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\IMG_9011870663240186505.jpg", "shottime", datetime.datetime(2018,4,18,23,34,24))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\IMG_9011870663240186505_1.jpg", "shottime", datetime.datetime(2018,4,18,23,34,24))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\pi3_gpio-1.png", "shottime", datetime.datetime(2018,10,24,11,22,43,180314))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\Screenshot_20180921-125001_Chrome.jpg", "shottime", datetime.datetime(2018,9,21,12,50,1))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\Screenshot_20181010-134856_Mi Home.jpg", "shottime", datetime.datetime(2018,10,10,13,48,56))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\Screenshot_20181010-145057_Mi Home.jpg", "shottime", datetime.datetime(2018,10,10,14,50,57))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\\temp_20_00_52_893.jpg", "shottime", datetime.datetime(2018,1,4,20,1,1))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\VideoCapture_20180615-110840.jpg", "shottime", datetime.datetime(2018,6,15,11,8,40))
        self.assertMeta(ctx, "CRED", "../camera-OpenCV-data/Mobile\VideoCapture_20180615-110840_1.jpg", "shottime", datetime.datetime(2018,6,15,11,8,40))

    def assertMeta(self, ctx: dict, unitKey: str, itemKey: str, paramKey: str, expected):
        print(itemKey)
        self.assertEqual(expected, ctx['meta'][unitKey][itemKey][paramKey])

    def test_CopySimulation(self):
        # python -m unittest tests.test_arch_photos.TestArchPhotos.test_CopySimulation
        pipeline = Pipeline()
        pipeline.providers.append(FilesWalkerProvider("../camera-OpenCV-data/Mobile/Lilia"))
        pipeline.processors.append(MediaCreationDateProcessor())
        pipeline.processors.append(PhotosArrangeProcessor('Mobile Lilia', isSimulation=True))

        ctx = {}
        pipeline.Get(ctx)
        pipeline.Process(ctx)

        files = ctx['items']
        # for file in ctx['meta']['PHOT']:
        #     arch_path = ctx['meta']['PHOT'][file]['arch_path']
        #     print(f'self.assertMeta(ctx, "PHOT", "{file}", "arch_path", "{arch_path}")')
        self.assertEqual(20, len(files))
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\18-04-29 19_01_07.png", "arch_path", "C:\\Src\\temp\\2018/18-04 Mobile Lilia\\18-04-29 19_01_07.png")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\1OTL16~B.PNG", "arch_path", "C:\\Src\\temp\\2019/19-05 Mobile Lilia\\1OTL16~B.PNG")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\1R1QVM~Q.PNG", "arch_path", "C:\\Src\\temp\\2018/18-04 Mobile Lilia\\1R1QVM~Q.PNG")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\20180223_224011.jpg", "arch_path", "C:\\Src\\temp\\2018/18-02 Mobile Lilia\\20180223_224011.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\20180730_100955.jpg", "arch_path", "C:\\Src\\temp\\2018/18-07 Mobile Lilia\\20180730_100955.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\20181031_120253.jpg", "arch_path", "C:\\Src\\temp\\2018/18-10 Mobile Lilia\\20181031_120253.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\20181031_120253_1.jpg", "arch_path", "C:\\Src\\temp\\2018/18-10 Mobile Lilia\\20181031_120253_1.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\DSC_0082.JPG", "arch_path", "C:\\Src\\temp\\2018/18-01 Mobile Lilia\\DSC_0082.JPG")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\DSC_0083.JPG", "arch_path", "C:\\Src\\temp\\2018/18-01 Mobile Lilia\\DSC_0083.JPG")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\IMG_20190208_203204.jpg", "arch_path", "C:\\Src\\temp\\2019/19-02 Mobile Lilia\\IMG_20190208_203204.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\IMG_20190208_203211.jpg", "arch_path", "C:\\Src\\temp\\2019/19-02 Mobile Lilia\\IMG_20190208_203211.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\IMG_20190623_144604.jpg", "arch_path", "C:\\Src\\temp\\2019/19-06 Mobile Lilia\\IMG_20190623_144604.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\IMG_20190623_144604_1.jpg", "arch_path", "C:\\Src\\temp\\2019/19-06 Mobile Lilia\\IMG_20190623_144604_1.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\MOV_0050.mp4", "arch_path", "C:\\Src\\temp\\2017/17-12 Mobile Lilia\\MOV_0050.mp4")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\PHOTO_20190929_150228.jpg", "arch_path", "C:\\Src\\temp\\2019/19-09 Mobile Lilia\\PHOTO_20190929_150228.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\PHOTO_20190929_154839.jpg", "arch_path", "C:\\Src\\temp\\2019/19-09 Mobile Lilia\\PHOTO_20190929_154839.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\Screenshot_20181010-135356.png", "arch_path", "C:\\Src\\temp\\2018/18-10 Mobile Lilia\\Screenshot_20181010-135356.png")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\scv_1533828457895555310231.jpg", "arch_path", "C:\\Src\\temp\\2018/18-08 Mobile Lilia\\scv_1533828457895555310231.jpg")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\VIDEO_20191224_201131.mp4", "arch_path", "C:\\Src\\temp\\2019/19-12 Mobile Lilia\\VIDEO_20191224_201131.mp4")
        self.assertMeta(ctx, "PHOT", "../camera-OpenCV-data/Mobile/Lilia\\VID_20190216_194013.mp4", "arch_path", "C:\\Src\\temp\\2019/19-02 Mobile Lilia\\VID_20190216_194013.mp4")


