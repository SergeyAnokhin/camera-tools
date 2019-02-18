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
# app.run(host='127.0.0.1', port=99)
yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')

@app.route('/')
def health():
    return 'OK'

@app.route('/analyse')
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
