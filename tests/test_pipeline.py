# run with :
# python -m unittest tests.test_pipeline.TestPipeline.test_DiffContoursProcessor
# python -m unittest discover     
import unittest, datetime, logging
import numpy as np
import pprint as pp
from copy import copy, deepcopy
from Providers.ImapShotsProvider import ImapShotsProvider
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Pipeline.ShotsPipeline import ShotsPipeline
from Pipeline.Model.PipelineShot import PipelineShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig

class TestPipeline(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', 
            level=logging.DEBUG, datefmt='%H:%M:%S')
        self.log = logging.getLogger("TEST")
        self.log.info('start %s: %s', __name__, datetime.datetime.now())

    def test_imapShotsProvider(self):
        target = ImapShotsProvider('temp')
        shots = target.GetShots('camera/foscam')
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].filename)
        self.assertIsNotNone(shots[0].fullname)
        self.assertIsNotNone(shots[0].Exist())

    def test_DirectoryShotsProvider(self):
        target = DirectoryShotsProvider.FromDir(None, 'temp')
        shots = target.GetShots(datetime.datetime.now)
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].filename)
        self.assertIsNotNone(shots[0].fullname)
        self.assertIsNotNone(shots[0].Exist())
        #shots[0].Show()

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
        pipeline = ShotsPipeline()
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(MailSenderProcessor(True))
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = pipeline.Process(shots)

        sendMeta = result[0].Metadata['IMAP']
        self.assertEqual(sendMeta["Subject"], "SUBJECT")
        self.assertEqual(sendMeta["Body"], "BODY")
        self.assertGreater(sendMeta["MessageSize"], 200000)

    def test_Archiveage(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_Archiveage
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        pipeline = ShotsPipeline('Foscam')
        pipeline.processors.append(DiffContoursProcessor())
        pipeline.processors.append(SaveToTempProcessor())
        pipeline.processors.append(ArchiveProcessor())
        pipeline.PreLoad()

        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = pipeline.Process(shots)

        meta = result[0].Metadata
        self.assertEqual(meta['TEMP']['fullname'], "temp/20190206-090254-foscam.jpg")
        self.assertEqual(meta['TEMP']['filename'], "20190206-090254-foscam.jpg")
        self.assertEqual(meta['TEMP']['filenameWithoutExtension'], "20190206-090254-foscam")
        self.assertEqual(meta['TEMP']['fullnameWithoutExtension'], "temp/20190206-090254-foscam")
        meta = result[1].Metadata
        self.assertEqual(meta['TEMP']['fullname'], "temp/20190206-090255-foscam.jpg")
        meta = result[2].Metadata
        self.assertEqual(meta['TEMP']['fullname'], "temp/20190206-090256-foscam.jpg")



    def test_WholePipeline(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_WholePipeline
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'

        ## INIT
        pipeline = ShotsPipeline()
        # # proceccor : Analyse() GetJsonResult() Draw()  
        #pipeline.processors.append(ZonesProcessor())
        pipeline.processors.append(DiffContoursProcessor())
        #pipeline.processors.append(MagnifyProcessor())
        pipeline.processors.append(YoloObjDetectionProcessor())
        pipeline.processors.append(TrackingProcessor())
        # #post processors:

        ########################################################################
        # Save analysed files to temp 
        # original: temp\20190203-085908-{camera}-{n}.jpg 
        # analysed: temp\20190203-085908-{camera}-{n}.(jpeg|png)
        # pipeline.processors.append(SaveToTempProcessor())           

        ########################################################################
        # save original files and analysed to archive directory by date
        # move from local archive to distant server (windows => diskstation) 
        # original: {ARCHIVE}\2019\02\03\20190203-085908-{camera}-{n}.jpg 
        # analysed: {ARCHIVE}\2019\02\03\20190203-085908-{camera}-{n}.(jpeg|png)
        # pipeline.processors.append(ArchiveProcessor())           

        ########################################################################
        # mail analysed files to gmail
        # attached: {ARCHIVE}\2019\02\03\cv_20190203-085908-{camera}-{n}.(jpeg|png)
        # attached: info.json 
        # body    : Analysis Log 
        # Subject : {HH:MM} {detected objects} {total_area_countours}
        # pipeline.processors.append(MailSenderPostProcessor())    

        ########################################################################
        # add to ES info about files + analysed info
        # pipeline.processors.append(ElasticSearchPostProcessor()) 

        ########################################################################
        # update files in hassio server
        # pipeline.processors.append(HassioPostProcessor())        

        pipeline.PreLoad()

        ## Procerss on shots comming
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = pipeline.Process(shots)
        # analyseResult[0].Shot.Show()
        # analyseResult[1].Shot.Show()
        # analyseResult[2].Shot.Show()
        #metadata1 = pipelineShots[1].Metadata["TRAC"]
        pp.pprint(result[1].Metadata)
        self.assertTrue("TRAC" in result[1].Metadata)
        self.assertTrue("YOLO" in result[1].Metadata)
        self.assertTrue("DIFF" in result[1].Metadata)
        self.assertTrue("TRAC" in result[2].Metadata)
        self.assertTrue("YOLO" in result[2].Metadata)
        self.assertTrue("DIFF" in result[2].Metadata)
