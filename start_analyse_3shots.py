import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from Common.GmailContext import GmailContext
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext


temp = 'temp'
# # Snap_20190214-080859-0.jpg => MDAlarm_20190214-080859.jpg
# gmail = GmailContext()
# gmail.Connect()
# mail = gmail.GetLastMail('camera/foscam')
# gmail.SaveAttachments(mail, temp + '/MDAlarm_{:%Y%m%d-%H%M%S}-{}.jpg')
# gmail.Disconnect()

#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')
yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')

shots = ThreeShots.FromDir(None, temp)

yoloResult = yolo.ProcessShot(shots.shot1)
yolo.drawRegions(shots.shot1.image_contours, yoloResult)
yoloResult = yolo.ProcessShot(shots.shot2)
yolo.drawRegions(shots.shot2.image_contours, yoloResult)
yoloResult = yolo.ProcessShot(shots.shot3)
yolo.drawRegions(shots.shot3.image_contours, yoloResult)

shots.CalcContours()

shots.shot1.DrawContours()
shots.shot2.DrawContours()
shots.shot3.DrawContours()

shots.shot1.MagnifyMotion()
shots.shot2.MagnifyMotion()
shots.shot3.MagnifyMotion()

shots.CreateWindow()

plt.subplot(shots.gs1[2])
shots.shot1.show_plt()
plt.subplot(shots.gs1[5])
shots.shot3.show_plt()

plt.subplot(shots.gs1[:2,:2]) # 
shots.shot2.show_plt()

shots.Save(temp + '/MDAlarm_{:%Y%m%d-%H%M%S}-cts.jpg')
shots.Show()
