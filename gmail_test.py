from GmailContext import GmailContext
from ThreeShots import ThreeShots
from YoloContext import YoloContext
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

temp = 'temp'
# gmail = GmailContext()
# gmail.Connect()
# gmail.GetLastMailAtachments('camera/foscam', attachments_path)
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

shots.Show()
shots.Save(os.path.join(temp, 'result.jpg'))