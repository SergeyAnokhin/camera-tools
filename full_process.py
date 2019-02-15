'''
0. New Mail Detected: sensor en Home Assisatant invoke run process
1. Download Mail From GMail
2. Save to local temp directory
3. Analyse shots
4. Copy to archive
5. Send data to Elasticsearch
'''
from Common.GmailContext import GmailContext
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext

temp = 'temp'
imap_folder = 'camera/foscam'

gmail = GmailContext()
gmail.DownoadLastAttachments(imap_folder, temp)

yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')

shots = ThreeShots.FromDir(temp)
shots.yoloContext = yolo
shots.Process(temp)
