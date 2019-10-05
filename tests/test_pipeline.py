# run with :
# python -m unittest tests.test_pipeline.TestPipeline.test_DiffContoursProcessor
# python -m unittest discover     
import unittest, datetime, logging, os, json
import numpy as np
import pprint as pp
import sys
from copy import copy, deepcopy
from Providers.ImapShotsProvider import ImapShotsProvider
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Processors.HassioProcessor import HassioProcessor
from Processors.ElasticSearchProcessor import ElasticSearchProcessor
from Pipeline.ShotsPipeline import ShotsPipeline
from Pipeline.Model.PipelineShot import PipelineShot
from Pipeline.Model.CamShot import CamShot
from Archiver.CameraArchiveHelper import CameraArchiveHelper

class TestPipeline(unittest.TestCase):

    def setUp(self):
        file_handler = logging.FileHandler(filename='processing.log')
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
            level=logging.DEBUG, 
            datefmt='%H:%M:%S',
            handlers=handlers)

        self.log = logging.getLogger("TEST")
        self.log.info(' ##################### ==> ')
        self.log.info('start %s: %s', __name__, datetime.datetime.now())
        self.archiver = CameraArchiveHelper()

    def test_imapShotsProvider(self):
        target = ImapShotsProvider('temp')
        shots = target.GetShots('camera/foscam')
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].filename)
        self.assertIsNotNone(shots[0].fullname)
        self.assertIsNotNone(shots[0].Exist())

    def test_DirectoryShotsProvider(self):
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = DirectoryShotsProvider.FromDir(None, folder)
        shots = target.GetShots()
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].filename)
        self.assertIsNotNone(shots[0].fullname)
        self.assertIsNotNone(shots[0].Exist())
        #shots[0].Show()

    def test_DirectoryShotsProvider_SearchByDate(self):
        folder = '../camera-OpenCV-data/Camera/Foscam/'
        baseShot = os.path.join(folder, 'Day_Lilia_Gate/Snap_20190206-090254-0.jpg')
        shot = CamShot(baseShot)
        shot.LoadImage()
        pShot = PipelineShot(shot, 0)
        pShot.Metadata['IMAP'] = {}
        pShot.Metadata['IMAP']['datetime'] = str(shot.GetDatetime())

        pShots = [ pShot ]
        target = DirectoryShotsProvider()
        target.config = self.archiver.load_configs('configs', [ 'Foscam' ])[0]
        pShots = target.GetShots(pShots)

        # search in C:\Src\camera-OpenCV-data\Camera\Foscam\2019-02\06
        self.assertEqual('Snap_20190206-090254-0.jpg', pShots[0].Shot.filename)
        self.assertEqual('MDAlarm_20190206-090259.jpg', pShots[1].Shot.filename)
        self.assertEqual('MDAlarm_20190206-090304.jpg', pShots[2].Shot.filename)

    def test_DiffContoursProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_DiffContoursProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = DiffContoursProcessor()
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        pipelineShots = [PipelineShot(shot) for shot in shots]

        target.Process(pipelineShots)
        pp.pprint(pipelineShots[0].Metadata, indent=2)
        pp.pprint(pipelineShots[1].Metadata, indent=2)
        pp.pprint(pipelineShots[2].Metadata, indent=2)
        # result[0].Shot.Show()
        # result[1].Shot.Show()
        # result[2].Shot.Show()
        metadata = pipelineShots[0].Metadata['DIFF']
        self.assertGreater(metadata['Diff']['TotalArea'], 5000)
        self.assertLess(metadata['Diff']['TotalArea'], 6000)
        self.assertEqual(len(metadata['boxes']), 2)
        self.assertGreater(metadata['boxes'][0]['area'], 5000)
        self.assertLess(metadata['boxes'][0]['area'], 6000)

    def test_YoloObjDetectionProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_YoloObjDetectionProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = YoloObjDetectionProcessor()
        target.PreLoad()
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        pipelineShots = [PipelineShot(shot) for shot in shots]
        target.Process(pipelineShots)
        metadata0 = pipelineShots[0].Metadata['YOLO']
        metadata1 = pipelineShots[1].Metadata['YOLO']
        metadata2 = pipelineShots[2].Metadata['YOLO']
        pp.pprint(metadata0, indent=2)
        self.assertEqual(len(metadata0), 1)
        self.assertEqual(len(metadata1), 1)
        self.assertEqual(len(metadata2), 1)
        self.assertEqual(metadata0[0]['label'], 'person')
        self.assertEqual(metadata1[0]['label'], 'person')
        self.assertEqual(metadata2[0]['label'], 'person')
        #pipelineShots[0].Shot.Show()

    def test_TrackingProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        yolo = YoloObjDetectionProcessor()
        yolo.PreLoad()
        target = TrackingProcessor()
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        pipelineShots = [PipelineShot(shot) for shot in shots]
        yolo.Process(pipelineShots)
        target.Process(pipelineShots)
        metadata1 = pipelineShots[1].Metadata["TRAC"]
        pp.pprint(metadata1, indent=2)
        # pipelineShots[1].Shot.Show()
        self.assertEqual(15, metadata1[0]['angle'])
        self.assertEqual(138, metadata1[0]['distance'])

    def test_MailSend(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_MailSend
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        pipeline = ShotsPipeline('Foscam')
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(MailSenderProcessor(True))
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = pipeline.Process(shots)

        sendMeta = result[0].Metadata['IMAP']
        self.assertEqual(sendMeta["Subject"], "Foscam @09:02 ")
        self.assertEqual(sendMeta["Body"], "BODY")
        self.assertGreater(sendMeta["MessageSize"], 200000)

    def test_ArchiveProcessor(self):
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        pipeline = ShotsPipeline('Foscam')
        pipeline.processors.append(ArchiveProcessor(True))
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = pipeline.Process(shots)

        archMD = result[0].Metadata['ARCH']
        self.assertEqual(archMD['archive_destination'], '\\\\diskstation\\CameraArchive\\Foscam\\2019-02\\06\\20190206_090254_Foscam_cv.jpeg')
        self.assertEqual(archMD['archive_destination_orig'], '\\\\diskstation\\CameraArchive\\Foscam\\2019-02\\06\\20190206_090254_Foscam.jpg')

    def test_SaveToTemp(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_Archiveage
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        pipeline = ShotsPipeline('Foscam')
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(SaveToTempProcessor())
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
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
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        pipeline = ShotsPipeline('Foscam')
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(ArchiveProcessor(True))
        pipeline.processors.append(ElasticSearchProcessor(True))
        #pipeline.processors.append(SaveToTempProcessor())
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
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
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        hassioDir = "temp"
        if not os.path.exists(hassioDir):
            os.mkdir(hassioDir)

        ## INIT
        pipeline = ShotsPipeline('Foscam')
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
        pipeline.processors.append(SaveToTempProcessor())           

        ########################################################################
        # mail analysed files to gmail
        # attached: {ARCHIVE}\2019\02\03\cv_20190203-085908-{n}-{camera}_cv.(jpeg|png)
        # attached: info.json 
        # body    : Analysis Log 
        # Subject : {HH:MM} {detected objects} {total_area_countours}
        pipeline.processors.append(MailSenderProcessor(True))    

        ########################################################################
        # update files in hassio server
        hassio = HassioProcessor()
        hassio.hassLocation = hassioDir
        pipeline.processors.append(hassio)        

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
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
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
        self.assertEqual(tempMD['original_fullname'], "temp\\20190328_080122_Foscam.jpg")
        tempMD = result[1].Metadata['TEMP']
        self.assertEqual(tempMD['fullname'], "temp\\20190328_080123_Foscam_cv.jpeg")
        self.assertEqual(tempMD['original_fullname'], "temp\\20190328_080123_Foscam.jpg")

        mailMD = result[0].Metadata['IMAP']
        self.assertEqual(mailMD["Subject"], "Foscam @08:01 person:2")
        #self.assertEqual(mailMD["Body"], "/** Processing LOG **/")
        self.assertGreater(mailMD["MessageSize"], 200000)

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
        self.assertEqual(dictEls['Analyse']['YOLO'][0]['label'], "person")
        self.assertEqual(dictEls['Analyse']['IMAP']['Subject'], "Foscam @08:01 person:2 / 2019-03-28")
