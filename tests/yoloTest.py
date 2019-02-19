import unittest
import json
import threading
from datetime import datetime
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext

class YoloTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(YoloTest, self).__init__(*args, **kwargs)
        print('start: {}'.format(datetime.now()))
        self.yolo = YoloContext('../camera-OpenCV-data/weights/yolov3-tiny')
        #self.yolo = YoloContext('../camera-OpenCV-data/weights/yolo-coco')

    def test_day_lilia_simple(self):
        print('start: {}'.format(datetime.now()))
        temp = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_simple'
        shots = ThreeShots.FromDir(None, temp)
        shots.yoloContext = self.yolo
        analyseData = shots.Analyse()
        #shots.Show()
        print(json.dumps(analyseData.__dict__, indent=4))
        self.assertIsNotNone(analyseData)


if __name__ == '__main__':
    unittest.main()