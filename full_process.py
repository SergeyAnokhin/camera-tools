'''
0. New Mail Detected: sensor en Home Assisatant invoke run process
1. Download Mail From GMail. Save to local temp directory
2. Analyse shots
3. Send mail with analyse and log
4. Copy to archive & Send data to Elasticsearch
'''
import os
from Common.GmailContext import GmailContext
from Common.ImapGmailHelper import ImapGmailHelper
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext

temp = 'temp'
imap_folder = 'camera/foscam'
camera = 'Foscam'
os.removedirs(temp)

### 1. Download Mail From GMail
gmail = GmailContext()
gmail.DownoadLastAttachments(imap_folder, temp)

### 2. Analyse shots
yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')
shots = ThreeShots.FromDir(None, temp)
shots.yoloContext = yolo
analyseData = shots.Analyse()
shots.Save(os.path.join(temp, 'MDAlarm_{:%Y%m%d-%H%M%S}-cts.jpg'))
shots.Show()

### 3. Send mail with analyse and log
imap = ImapGmailHelper()
mail_subject = "{} @{:%H:%M} motion detected".format(camera, shots.shot1.datetime)
imap.send_mail(mail_subject, "(log must be here)", [shots.output_filename])

### 4. Copy to archive & Send data to Elasticsearch
# filesToArchive = shots.GetFullNamesArray()
# archiver = Archiver()
# config = archiver.LoadConfig(camera)
# archiver.Send(config, filesToArchive, analyseData)
