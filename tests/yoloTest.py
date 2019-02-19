import unittest

class YoloTest(unittest.TestCase):

    def __init__(self):
        imap_folder = 'camera/foscam'
        camera = 'Foscam'
        print('start: {}'.format(datetime.datetime.now()))
        #yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
        yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def SimpleTest(self):
        temp = '../camera-OpenCV-data/Camera/Foscam/Day_Lilia_Gate'

        shots = ThreeShots.FromDir(None, temp)
        shots.yoloContext = yolo
        analyseData = shots.Analyse()

        self.assertIsNotNone(analyseData)

if __name__ == '__main__':
    unittest.main()