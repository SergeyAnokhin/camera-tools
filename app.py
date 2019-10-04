from flask import Flask
from flask import request
import logging, os, json, datetime, shutil, threading, sys
from Common.GmailContext import GmailContext
from Common.ImapGmailHelper import ImapGmailHelper
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Processors.HassioProcessor import HassioProcessor
from Processors.ElasticSearchProcessor import ElasticSearchProcessor
from Pipeline.Model.PipelineShot import PipelineShot
from Pipeline.ShotsPipeline import ShotsPipeline


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

file_handler = logging.FileHandler(filename='camera-tools-api.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
    level=logging.DEBUG, 
    datefmt='%H:%M:%S',
    handlers=handlers)

log = logging.getLogger("API")
log.info('start API @ %s', datetime.datetime.now())


app = Flask(__name__)
print('start: {}'.format(datetime.datetime.now()))
if __name__ == "__main__":
    print('app.run @ 5000')
    app.run(host='192.168.1.31', port=5000)
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')
lock = threading.Lock()

pipeline = ShotsPipeline('Foscam')
pipeline.processors.append(DiffContoursProcessor())
pipeline.processors.append(YoloObjDetectionProcessor())
pipeline.processors.append(TrackingProcessor())
pipeline.processors.append(SaveToTempProcessor())           
pipeline.processors.append(MailSenderProcessor(True))    
pipeline.processors.append(HassioProcessor('temp'))        
pipeline.processors.append(ArchiveProcessor(True))
pipeline.processors.append(ElasticSearchProcessor(True)) 
pipeline.PreLoad()

log.info('initialization API finished @ %s', datetime.datetime.now())

@app.route('/', methods=['GET'])
def health():
    return 'OK'

@app.route('/V2/test', methods=['GET'])
def testV2():
    ### INIT
    lock.acquire()
    log.info('start endpoint /V2/test')
    folder = '../camera-OpenCV-data/Camera/Foscam/Day_Sergey_and_Olivia_tracking'

    ### RUN
    shots = DirectoryShotsProvider.FromDir(None, folder).GetShots(datetime.datetime.now)
    result = pipeline.Process(shots)

    ### FINISH
    lock.release()
    log.info('end endpoint /V2/test')
    return 'OK' # json.dumps(result[0].Metadata)

@app.route('/analyse', methods=['GET'])
def analyse():
    lock.acquire()

    ### 1. Download Mail From GMail
    gmail = GmailContext()
    if os.path.exists(temp):
        shutil.rmtree(temp)
    gmail.DownoadLastAttachments(imap_folder, temp)

    ### 2. Analyse shots
    shots = ThreeShots.FromDir(None, temp)
    ###### shots.yoloContext = yolo
    analyseData = shots.Analyse()
    shots.Save(os.path.join(temp, 'MDAlarm_{:%Y%m%d-%H%M%S}-cts.jpg'))
    #shots.Show()

    ### 3. Send mail with analyse and log
    imap = ImapGmailHelper()
    mail_subject = "{} @{:%H:%M} motion detected".format(camera, shots.shot1.datetime)
    imap.send_mail(mail_subject, analyseData.GetMailBody(), [shots.output_filename])
    lock.release()
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
