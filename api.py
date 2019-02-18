from flask import Flask
from flask import request
import datetime
import os
import shutil
from Common.GmailContext import GmailContext
from Common.ImapGmailHelper import ImapGmailHelper
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext


'''
run locally :
> set FLASK_APP=api.py
> flask run
    -OR-
> run.cmd
'''

temp = 'temp'
imap_folder = 'camera/foscam'
camera = 'Foscam'

app = Flask(__name__)
print('start: {}'.format(datetime.datetime.now()))
if __name__ == "__main__":
    print('app.run @ 5000')
    app.run(host='192.168.1.31', port=5000)
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')

@app.route('/', methods=['GET'])
def health():
    return 'OK'

@app.route('/test1', methods=['GET'])
def test1():
    return 'OK'

@app.route('/test2', methods=['GET'])
def test2():
    return 'OK'

@app.route('/analyse', methods=['GET'])
def analyse():
    ### 1. Download Mail From GMail
    gmail = GmailContext()
    if os.path.exists(temp):
        shutil.rmtree(temp)
    gmail.DownoadLastAttachments(imap_folder, temp)

    ### 2. Analyse shots
    shots = ThreeShots.FromDir(None, temp)
    shots.yoloContext = yolo
    analyseData = shots.Analyse()
    shots.Save(os.path.join(temp, 'MDAlarm_{:%Y%m%d-%H%M%S}-cts.jpg'))
    #shots.Show()

    ### 3. Send mail with analyse and log
    imap = ImapGmailHelper()
    mail_subject = "{} @{:%H:%M} motion detected".format(camera, shots.shot1.datetime)
    imap.send_mail(mail_subject, "(log must be here)", [shots.output_filename])
    return 'OK'

# @app.route('/fit', methods=['POST'])
# def fit():
#     return presentor.fit(request.data)

# @app.route('/predict', methods=['POST'])
# def predict():
#     return presentor.predict(request.data)

# @app.route('/fitTest', methods=['GET'])
# def fitTest():
#     return presentor.fit(cHelper.ReadFile('fitTest.json'))
