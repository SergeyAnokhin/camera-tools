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
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = DiffContoursProcessor()
        target.Shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = target.Process()
        pp.pprint(result[0].Summary, indent=2)
        self.assertEqual(result[0].Summary[0]['label'], 'person')
        result[0].Shot.Show()
        # result[1].Show()
        # result[2].Show()

    def test_YoloObjDetectionProcessor(self):
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'
        target = YoloObjDetectionProcessor()
        target.Shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        result = target.Process()
        pp.pprint(result.Summary[0], indent=2)
        result.Shots[0].Show()

    def test_TrackingProcessor(self):
        # python -m unittest tests.test_pipeline.TestPipeline.test_TrackingProcessor
        folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'
        result = {}
        yolo = YoloObjDetectionProcessor()
        target = TrackingProcessor()
        shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
        yolo.Shots = shots
        target.Shots = shots
        result['YoloObjDetectionProcessor'] = yolo.Process()
        result['TrackingProcessor'] = target.Process(result)
        #pp.pprint(result['TrackingProcessor'].Summary[0], indent=2)
        result['TrackingProcessor'].Shots[0].Show()
        result['TrackingProcessor'].Shots[1].Show()
        result['TrackingProcessor'].Shots[2].Show()

