'''
0. New Mail Detected: sensor en Home Assisatant invoke run process
1. Download Mail From GMail. Save to local temp directory
2. Analyse shots
3. Copy to archive
4. Send data to Elasticsearch
'''
from Common.GmailContext import GmailContext
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext

temp = 'temp'
imap_folder = 'camera/foscam'

### 1. Download Mail From GMail
gmail = GmailContext()
gmail.DownoadLastAttachments(imap_folder, temp)

### 2. Analyse shots
yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
shots = ThreeShots.FromDir(None, temp)
shots.yoloContext = yolo
shots.Process(temp)

### 3. Copy to archive
# convert Shot => FileArchiveInfo

### 4. Send data to Elasticsearch
