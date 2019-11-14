# run with :
# python -m unittest tests.test_pipeline.TestPipeline.test_DiffContoursProcessor
# python -m unittest discover     
import unittest, datetime, logging, os, json, subprocess
import numpy as np
import pprint as pp
import sys
from copy import copy, deepcopy
from Providers.ImapShotsProvider import ImapShotsProvider
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Providers.ElasticSearchProvider import ElasticSearchProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Processors.HassioProcessor import HassioProcessor
from Processors.ElasticSearchProcessor import ElasticSearchProcessor
from Common.CommonHelper import CommonHelper
from Common.SecretConfig import SecretConfig
from tests.TestProcessor import TestProcessor
from Pipeline.ShotsPipeline import ShotsPipeline
from Pipeline.Model.PipelineShot import PipelineShot
from Pipeline.Model.CamShot import CamShot
from Archiver.CameraArchiveHelper import CameraArchiveHelper

class TestPipeline(unittest.TestCase):
    log: logging.Logger = None

    def __init__(self, *args, **kwargs):
        super(TestPipeline, self).__init__(*args, **kwargs)
        file_handler = logging.FileHandler(filename='test.log', mode='w')
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
            level=logging.DEBUG, 
            datefmt='%H:%M:%S',
            handlers=handlers)
        self.log = logging.getLogger("TEST")
        TestPipeline.log = self.log
        self.archiver = CameraArchiveHelper()
        self.helper = CommonHelper()
        self.helper.GetNetworkConfig()
        CommonHelper.networkConfig['camera_live_archive'] = ""
        CommonHelper.networkConfig['camera_archive_archive'] = ""
        self.log.info('')
        self.log.info(' ############################ ')
        self.log.info(' ### SETUP ################## ')
        self.log.info(' ############################ ')

    def setUp(self):
        self.log.info(f' ### SETUP {self._testMethodName} ################## ==> ')
        self.log.info('start %s: %s', __name__, datetime.datetime.now())

    def tearDown(self):
        self.log.info(f' ### TEARDOWN {self._testMethodName} ############### <== ')

    @classmethod
    def tearDownClass(self):
        TestPipeline.log.info(' ############################ ')
        TestPipeline.log.info(' ### TEARDOWN ############### ')
        TestPipeline.log.info(' ############################ ')

    def test_imapShotsProvider(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_imapShotsProvider
        target = ImapShotsProvider('temp/queue')
        target.config = self.archiver.load_configs('configs', [ 'Foscam' ])[0]
        shots = target.GetShots([])
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].Shot.filename)
        self.assertIsNotNone(shots[0].Shot.fullname)
        self.assertIsNotNone(shots[0].Shot.Exist())
        #self.assertEqual(shots[0].Metadata['PROV:IMAP']['filename'], 'Snap_20191028-192355-0.jpg')
        start = shots[0].Metadata['PROV:IMAP']['start']
        self.assertEqual(shots[1].Metadata['PROV:IMAP']['start'], start)
        self.assertEqual(shots[2].Metadata['PROV:IMAP']['start'], start)

    def test_DirectoryShotsProvider(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_DirectoryShotsProvider
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        shots = DirectoryShotsProvider.FromDir(None, folder)
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].Shot.filename)
        self.assertIsNotNone(shots[0].Shot.fullname)
        self.assertIsNotNone(shots[0].Shot.Exist())
        #shots[0].Show()

    def test_DirectoryShotsProvider_SearchByDate(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_DirectoryShotsProvider_SearchByDate
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        pShots = DirectoryShotsProvider.FromDir(None, folder)

        # Create base Shot
        for pShot in pShots:
            pShot.Metadata['PROV:IMAP'] = {}
            pShot.Metadata['PROV:IMAP']['start'] = self.helper.ToTimeStampStr(pShot.Shot.GetDatetime())

        CommonHelper.networkConfig = {}
        CommonHelper.networkConfig['camera_archive_path'] = "../temp/CameraArchive"
        CommonHelper.networkConfig['camera_live_path'] = "../camera-OpenCV-data/Camera/Foscam"
        target = DirectoryShotsProvider()
        target.config = self.archiver.load_configs('configs', [ 'Foscam' ])[0]
        target.config.path_from = '2019-02'
        pShots = target.GetShots(pShots)

        # search in C:\Src\camera-OpenCV-data\Camera\Foscam\2019-02\06
        self.assertEqual('Snap_20190206-090254-0.jpg', pShots[0].Shot.filename)
        self.assertEqual('Snap_20190206-090254-1.jpg', pShots[1].Shot.filename)
        self.assertEqual('Snap_20190206-090254-2.jpg', pShots[2].Shot.filename)
        self.assertEqual('MDAlarm_20190206-090259.jpg', pShots[3].Shot.filename)
        self.assertEqual('MDAlarm_20190206-090304.jpg', pShots[4].Shot.filename)

    def test_DiffContoursProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_DiffContoursProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = DiffContoursProcessor()
        pipelineShots = DirectoryShotsProvider.FromDir(None, folder)

        target.Process(pipelineShots, {})
        # pp.pprint(pipelineShots[0].Metadata, indent=2)
        # pp.pprint(pipelineShots[1].Metadata, indent=2)
        # pp.pprint(pipelineShots[2].Metadata, indent=2)
        # result[0].Shot.Show()
        # result[1].Shot.Show()
        # result[2].Shot.Show()
        metadata = pipelineShots[0].Metadata['DIFF']
        self.assertGreater(metadata['Diff']['TotalArea'], 5000)
        self.assertLess(metadata['Diff']['TotalArea'], 6000)
        self.assertEqual(metadata['Diff']['Count'], 3)
        self.assertEqual(len(metadata['boxes']), 3)
        self.assertGreater(metadata['boxes'][0]['area'], 5000)
        self.assertLess(metadata['boxes'][0]['area'], 6000)

    def test_YoloObjDetectionProcessor_noObjects(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_YoloObjDetectionProcessor_noObjects
        # INIT
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_No_Objects'
        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(TestProcessor({ 'YOLO': { 'labels': 'person:2 car bird' } }))
        pipeline.processors.append(YoloObjDetectionProcessor())
        pipeline.PreLoad()

        # TEST
        shots = pipeline.GetShots()
        shots = pipeline.Process(shots)

        # ASSERT
        self.assertEqual(5, len(shots))
        self.assertEqual(shots[0].Shot.GetDatetime(), datetime.datetime(2019,10,16,14,21,48))
        self.assertEqual(shots[1].Shot.GetDatetime(), datetime.datetime(2019,10,16,14,21,50))
        self.assertEqual(shots[2].Shot.GetDatetime(), datetime.datetime(2019,10,16,14,21,52))
        self.assertEqual(shots[3].Shot.GetDatetime(), datetime.datetime(2019,10,16,14,21,53))
        self.assertEqual(shots[4].Shot.GetDatetime(), datetime.datetime(2019,10,16,14,21,58))
        self.assertFalse('YOLO' in shots[0].Metadata)
        self.assertFalse('YOLO' in shots[1].Metadata)
        self.assertFalse('YOLO' in shots[2].Metadata)

    def test_YoloObjDetectionProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_YoloObjDetectionProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = YoloObjDetectionProcessor()
        target.PreLoad()
        shots = DirectoryShotsProvider.FromDir(None, folder)
        target.Process(shots, {})
        metadata0 = shots[0].Metadata['YOLO']
        metadata1 = shots[1].Metadata['YOLO']
        metadata2 = shots[2].Metadata['YOLO']
        pp.pprint(metadata0, indent=2)
        self.assertEqual(len(metadata0['areas']), 1)
        self.assertEqual(len(metadata1['areas']), 1)
        self.assertEqual(len(metadata2['areas']), 1)
        self.assertEqual(metadata0['areas'][0]['label'], 'person')
        self.assertEqual(metadata1['areas'][0]['label'], 'person')
        self.assertEqual(metadata2['areas'][0]['label'], 'person')
        self.assertEqual(metadata0['labels'], 'person')
        self.assertEqual(metadata1['labels'], 'person')
        self.assertEqual(metadata2['labels'], 'person')
        #pipelineShots[0].Shot.Show()

    def test_TrackingProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        yolo = YoloObjDetectionProcessor()
        yolo.PreLoad()
        target = TrackingProcessor(isDebug=True)
        pipelineShots = DirectoryShotsProvider.FromDir(None, folder)
        yolo.Process(pipelineShots, {})
        target.Process(pipelineShots, {})
        metadata1 = pipelineShots[1].Metadata["TRAC"]
        pp.pprint(metadata1, indent=2)
        pipelineShots[1].Shot.Show()
        self.assertEqual(15, metadata1[0]['angle'])
        self.assertEqual(138, metadata1[0]['distance'])
        self.assertEqual("372x122", metadata1[0]['center'])
        self.assertEqual(16, metadata1[1]['angle'])
        self.assertEqual(90, metadata1[1]['distance'])
        self.assertEqual("230x146", metadata1[1]['center'])

        metadata2 = pipelineShots[2].Metadata["TRAC"]
        pp.pprint(metadata2, indent=2)
        self.assertEqual(28, metadata2[0]['angle'])
        self.assertEqual(68, metadata2[0]['distance'])
        self.assertEqual("432x89", metadata2[0]['center'])
        self.assertEqual(10, metadata2[1]['angle'])
        self.assertEqual(94, metadata2[1]['distance'])
        self.assertEqual("323x129", metadata2[1]['center'])

    def test_TrackingProcessor2(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor2
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(YoloObjDetectionProcessor())
        pipeline.processors.append(TrackingProcessor(isDebug=True))
        pipeline.PreLoad()
        shots = pipeline.GetShots()
        result = pipeline.Process(shots)

        metadata1 = result[1].Metadata["TRAC"]
        pp.pprint(metadata1, indent=2)
        #result[1].Shot.Show()
        self.assertEqual(1, len(metadata1))
        self.assertEqual(25, metadata1[0]['angle'])
        self.assertEqual(94, metadata1[0]['distance'])
        self.assertEqual("289x101", metadata1[0]['center'])

        metadata2 = result[2].Metadata["TRAC"]
        pp.pprint(metadata2, indent=2)
        #result[2].Shot.Show()
        self.assertEqual(1, len(metadata2))
        self.assertEqual(10, metadata2[0]['angle'])
        self.assertEqual(89, metadata2[0]['distance'])
        self.assertEqual("377x84", metadata2[0]['center'])

    def test_TrackingProcessor_SizeError(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor_SizeError
        folder = '../camera-OpenCV-data/Camera/Foscam/Morning_Sergey_Tracking_Error'
        yolo = YoloObjDetectionProcessor()
        yolo.PreLoad()
        target = TrackingProcessor(isDebug=True)
        pipelineShots = DirectoryShotsProvider.FromDir(None, folder)
        yolo.Process(pipelineShots, {})
        target.Process(pipelineShots, {})
        metadata1 = pipelineShots[1].Metadata["TRAC"]
        pp.pprint(metadata1, indent=2)
        # pipelineShots[1].Shot.Show()
        self.assertEqual(15, metadata1[0]['angle'])
        self.assertEqual(138, metadata1[0]['distance'])

    def test_MailSend(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_MailSend
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(TestProcessor({ 'YOLO': { 'labels': 'person:2 car bird' } }))
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(MailSenderProcessor(True))
        pipeline.PreLoad()
        shots = pipeline.GetShots()
        shots[0].Metadata['YOLO'] = {}
        shots[1].Metadata['YOLO'] = {}
        shots[2].Metadata['YOLO'] = {}
        shots[0].Metadata['YOLO']['labels'] = "person:2 car"
        shots[1].Metadata['YOLO']['labels'] = "person bird car"
        shots[2].Metadata['YOLO']['labels'] = ""
        shots[0].Metadata['YOLO']['areas'] = [self.getYoloArea('person'), self.getYoloArea('person'), self.getYoloArea('car')]
        shots[1].Metadata['YOLO']['areas'] = [self.getYoloArea('person'), self.getYoloArea('bird'), self.getYoloArea('car')]
        shots[2].Metadata['YOLO']['areas'] = []

        result = pipeline.Process(shots)

        sendMeta = result[0].Metadata['SMTP']
        self.assertEqual(sendMeta["Subject"], "Foscam @09:02:54 person:2 car bird (06.02.2019)")
        self.assertEqual(sendMeta["id"], 'Foscam@2019-02-06T09:02:56.000Z')
        #self.assertEqual(sendMeta["Body"], "BODY")
        #self.assertGreater(sendMeta["MessageSize"], 200000)

    def getYoloArea(self, label:str):
        return {
            "area": 5562,
            "center_coordinate": [
                169,
                158
            ],
            "confidence": 0.99,
            "label": label,
            "profile_proportion": 1.91,
            "size": [
                54,
                103
            ]
        }

    def test_ArchiveProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_ArchiveProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        CommonHelper.networkConfig = {}
        CommonHelper.networkConfig['camera_archive_path'] = "../temp/CameraArchive"

        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(ArchiveProcessor(True))
        pipeline.PreLoad()

        shots = pipeline.GetShots()
        result = pipeline.Process(shots)

        archMD = result[0].Metadata['ARCH']
        self.assertEqual(archMD['archive_destination'], '../temp/CameraArchive\\Foscam\\2019-02\\06\\20190206_090254_Foscam_cv.jpeg')
        self.assertEqual(archMD['archive_destination_orig'], '../temp/CameraArchive\\Foscam\\2019-02\\06\\20190206_090254_Foscam.jpg')

    def test_SaveToTemp(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_SaveToTemp
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(SaveToTempProcessor(True))
        pipeline.PreLoad()

        shots = pipeline.GetShots()
        result = pipeline.Process(shots)

        self.assertEqual(result[0].Shot.fullname, "temp\\20190206_090254_Foscam_cv.jpeg")
        self.assertEqual(result[0].OriginalShot.fullname, "temp\\20190206_090254_Foscam.jpg")
        self.assertTrue(os.path.isfile(result[0].Shot.fullname))
        self.assertTrue(os.path.isfile(result[0].OriginalShot.fullname))
        self.assertEqual(result[1].Shot.fullname, "temp\\20190206_090255_Foscam_cv.jpeg")
        self.assertEqual(result[1].OriginalShot.fullname, "temp\\20190206_090255_Foscam.jpg")
        self.assertEqual(result[2].Shot.fullname, "temp\\20190206_090256_Foscam_cv.jpeg")
        self.assertEqual(result[2].OriginalShot.fullname, "temp\\20190206_090256_Foscam.jpg")

    def test_ElasticSearchProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_ElasticSearchProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        CommonHelper.networkConfig = {}

        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(ArchiveProcessor(True))
        pipeline.processors.append(ElasticSearchProcessor(True))
        #pipeline.processors.append(SaveToTempProcessor())
        pipeline.PreLoad()

        shots = pipeline.GetShots()
        result = pipeline.Process(shots)

        els = result[0].Metadata["ELSE"]
        self.assertIsNotNone(els['JSON'])
        #print(els['JSON'])
        dictEls = json.loads(els['JSON'])
        analyse = dictEls['Analyse']
        del dictEls['Analyse']

        expected = {
            "@timestamp": "2019-02-06T08:02:54.000Z",
            "camera": "Foscam",
            "doc": "event",
            "ext": "jpg",
            "path": "/CameraArchive/Foscam/2019-02/06/20190206_090254_Foscam.jpg",
            "position": {
                "detail": "under the roof",
                "floor": -1,
                "room": "FrontWall"
            },
            "sensor": {
                "device": "Foscam FI9805W",
                "display": "Foscam(.) FrontWall",
                "id": "FoscamCameraArchiveFI9805W_C4D6553DECE1",
                "is_external": True,
                "type": "CameraArchive",
                "unit": "bytes"
            },
            "tags": [
                "synology_cameraarchive",
                "camera_tools"
            ],
            "value": 69623,
            "volume": "/volume2"
        }

        for key in expected:
            self.assertEqual(dictEls[key], expected[key])

        self.assertAlmostEqual(analyse['DIFF']['boxes'][0]['profile_proportion'], 1.77, delta=0.01)

    def test_WholePipeline(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_WholePipeline
        CommonHelper.networkConfig = {}
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        hassioDir = "temp"
        if not os.path.exists(hassioDir):
            os.mkdir(hassioDir)

        ## INIT
        pipeline = ShotsPipeline('Foscam')
        pipeline.providers.append(DirectoryShotsProvider(folder))
        # # proceccor : Analyse() GetJsonResult() Draw()  
        #pipeline.processors.append(ZonesProcessor())
        pipeline.processors.append(DiffContoursProcessor())
        #pipeline.processors.append(MagnifyProcessor())
        pipeline.processors.append(YoloObjDetectionProcessor())
        pipeline.processors.append(TrackingProcessor())
        # #post processors:

        ########################################################################
        # Save analysed files to temp 
        # original: temp\20190203_085908_{camera}.jpg 
        # analysed: temp\20190203_085908_{camera}_cv.jpeg
        pipeline.processors.append(SaveToTempProcessor(True))           

        ########################################################################
        # mail analysed files to gmail
        # attached: {ARCHIVE}\2019\02\03\cv_20190203-085908-{n}-{camera}_cv.(jpeg|png)
        # attached: info.json 
        # body    : Analysis Log 
        # Subject : {HH:MM} {detected objects} {total_area_countours}
        pipeline.processors.append(MailSenderProcessor(True))    

        ########################################################################
        # update files in hassio server
        pipeline.processors.append(HassioProcessor(hassioDir))        

        ########################################################################
        # save original files and analysed to archive directory by date
        # move from local archive to distant server (windows => diskstation) 
        # original: {ARCHIVE}\2019\02\03\20190203-085908-{n}-{camera}.jpg 
        # analysed: {ARCHIVE}\2019\02\03\20190203-085908-{n}-{camera}_cv.(jpeg|png)
        pipeline.processors.append(ArchiveProcessor(True))

        ########################################################################
        # add to ES info about files + analysed info
        pipeline.processors.append(ElasticSearchProcessor(True)) 

        pipeline.PreLoad()

        ## Procerss on shots comming
        shots = pipeline.GetShots()
        result = pipeline.Process(shots)
        # analyseResult[0].Shot.Show()
        # analyseResult[1].Shot.Show()
        # analyseResult[2].Shot.Show()
        self.assertTrue("TRAC" in result[1].Metadata)
        self.assertTrue("YOLO" in result[1].Metadata)
        self.assertTrue("DIFF" in result[1].Metadata)
        self.assertTrue("TRAC" in result[2].Metadata)
        self.assertTrue("YOLO" in result[2].Metadata)
        self.assertTrue("DIFF" in result[2].Metadata)
        self.assertTrue("TEMP" in result[2].Metadata)
        self.assertTrue("HASS" in result[2].Metadata)
        self.assertTrue("ELSE" in result[2].Metadata)

        tempMD = result[0].Metadata['TEMP']
        self.assertEqual(tempMD['fullname'], "temp\\20190328_080122_Foscam_cv.jpeg")
        #self.assertEqual(tempMD['original_fullname'], "temp\\20190328_080122_Foscam.jpg")
        tempMD = result[1].Metadata['TEMP']
        self.assertEqual(tempMD['fullname'], "temp\\20190328_080123_Foscam_cv.jpeg")
        #self.assertEqual(tempMD['original_fullname'], "temp\\20190328_080123_Foscam.jpg")

        mailMD = result[0].Metadata['SMTP']
        self.assertEqual(mailMD["Subject"], "Foscam @08:01:22 person:2 (28.03.2019)")
        #self.assertEqual(mailMD["Body"], "/** Processing LOG **/")
        #self.assertGreater(mailMD["MessageSize"], 200000)

        hassMD = result[0].Metadata['HASS']
        self.assertEqual(hassMD['hassio_location'], 'temp\\cv_Foscam_0.jpg')

        archMD = result[0].Metadata['ARCH']
        self.assertEqual(archMD['archive_destination'], '\\\\diskstation\\CameraArchive\\Foscam\\2019-03\\28\\20190328_080122_Foscam_cv.jpeg')
        self.assertEqual(archMD['archive_destination_orig'], '\\\\diskstation\\CameraArchive\\Foscam\\2019-03\\28\\20190328_080122_Foscam.jpg')

        els = result[0].Metadata["ELSE"]
        self.assertIsNotNone(els['JSON'])
        dictEls = json.loads(els['JSON'])
        print(els['JSON'])
        self.assertIsNotNone(dictEls['Analyse'])
        self.assertEqual(dictEls['Analyse']['YOLO']['areas'][0]['label'], "person")
        self.assertEqual(dictEls['Analyse']['YOLO']['labels'], "person:2")
        self.assertEqual(dictEls['Analyse']['SMTP']['Subject'], "Foscam @08:01:22 person:2 (28.03.2019)")

    def test_ElasticSearchProvider(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_ElasticSearchProvider
        CommonHelper.networkConfig = {}
        target = ElasticSearchProvider("Foscam", datetime.datetime(2019, 10, 20, 17, 18, 8), True)
        result = target.GetShots([])
        meta = result[0].Metadata['PROV:ELSE']
        self.assertEqual("Foscam@2019-10-20T15:18:08.000Z", meta['id'])
        self.assertEqual("cameraarchive-2019", meta['index'])

    def test_secretConfig(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_secretConfig
        secretConfig = SecretConfig()
        secretConfig.fromJsonFile()

        network = self.helper.GetNetworkName()
        networkConfig = secretConfig.GetNetworkConfig(network)

        print(f'network: {network}; networkConfig: {networkConfig}')
        self.assertIsNotNone(networkConfig['elasticsearch'])
        self.assertTrue(network in networkConfig['network'])

if __name__ == '__main__':
    unittest.main()