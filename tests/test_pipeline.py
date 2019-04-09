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
from Pipeline.ShotsPipeline import ShotsPipeline
from PostProcessors.ArchivePostProcessor import ArchivePostProcessor
from PostProcessors.ElasticSearchPostProcessor import ElasticSearchPostProcessor
from PostProcessors.HassioPostProcessor import HassioPostProcessor
from PostProcessors.MailSenderPostProcessor import MailSenderPostProcessor
from Pipeline.Model.PipelineShot import PipelineShot

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
        pipelineShots[0].Shot.Show()

    def test_TrackingProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        yolo = YoloObjDetectionProcessor()
        yolo.PreLoad()
        target = TrackingProcessor()
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        target.PipelineResults['YoloObjDetectionProcessor'] = yolo.Process(shots)
        result = target.Process(shots)
        pp.pprint(result[1].Summary, indent=2)
        #result[1].Shot.Show()
        self.assertEqual(15, result[1].Summary[0]['angle'])
        self.assertEqual(138, result[1].Summary[0]['distance'])

    def test_WholePipeline(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_WholePipeline
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'

        ## INIT
        pipeline = ShotsPipeline()
        # # proceccor : Analyse() GetJsonResult() Draw()  
        pipeline.processors.append(DiffContoursProcessor())
        #pipeline.processors.append(MagnifyProcessor())
        pipeline.processors.append(YoloObjDetectionProcessor())
        pipeline.processors.append(TrackingProcessor())
        #post processors:
        pipeline.processors.append(MailSenderPostProcessor()) 
        pipeline.processors.append(ElasticSearchPostProcessor()) 
        pipeline.processors.append(ArchivePostProcessor()) 
        pipeline.processors.append(HassioPostProcessor()) 

        pipeline.PreLoad()

        ## Procerss on shots comming
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        pipelineShots = [PipelineShot(shot) for shot in shots]


        analyseResult = pipeline.Process(pipelineShots)
        pipeline.Show()
        pipeline.PostProcess()