from flask import Flask
from flask import request
from logging.handlers import TimedRotatingFileHandler
import logging, os, json, datetime, shutil, threading, sys
from Common.GmailContext import GmailContext
from Common.ImapGmailHelper import ImapGmailHelper
from OpenCV.ThreeShots import ThreeShots
from OpenCV.YoloContext import YoloContext
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Providers.ImapShotsProvider import ImapShotsProvider
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
> set FLASK_APP=app.py
> flask run
    -OR-
> run.cmd
'''

temp = 'temp'
imap_folder = 'camera/foscam'
camera = 'Foscam'
isSimulation = False

file_error_handler = logging.FileHandler(filename='camera-tools-error.log')
file_error_handler.setLevel(logging.ERROR)
file_handler = logging.handlers.TimedRotatingFileHandler('camera-tools.log', when='D', backupCount=7)
file_handler.suffix = '_%Y-%m-%d.log'
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler, file_error_handler]

logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
    level=logging.DEBUG, 
    datefmt='%H:%M:%S',
    handlers=handlers)

log = logging.getLogger("API")
log.info('|##########################################################################################################|')
log.info('|####### start API @ %s ###################################################################################|', datetime.datetime.now())
log.info('|##########################################################################################################|')

app = Flask(__name__)
print('start: {}'.format(datetime.datetime.now()))
if __name__ == "__main__":
    print('app.run @ 5000')
    app.run(host='192.168.1.31', port=5000)
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolov3-tiny')
#yolo = YoloContext('..\\camera-OpenCV-data\\weights\\yolo-coco')
lock = threading.Lock()

pipeline = ShotsPipeline('Foscam')
pipeline.providers.append(ImapShotsProvider())
pipeline.providers.append(DirectoryShotsProvider())
pipeline.processors.append(DiffContoursProcessor())
pipeline.processors.append(YoloObjDetectionProcessor())
pipeline.processors.append(TrackingProcessor())
pipeline.processors.append(SaveToTempProcessor())           
pipeline.processors.append(MailSenderProcessor(isSimulation))
pipeline.processors.append(HassioProcessor()) #('temp' if isSimulation else None))        
pipeline.processors.append(ArchiveProcessor(isSimulation))
pipeline.processors.append(ElasticSearchProcessor(isSimulation)) 
pipeline.PreLoad()

log.info('initialization API finished @ %s', datetime.datetime.now())

@app.route('/', methods=['GET'])
def health():
    return 'OK'

@app.route('/V2/analyse', methods=['GET'])
def analyseV2():
    ### INIT
    log.info('====== start endpoint /V2/analyse ============================================================================')

    ### RUN
    shots = pipeline.GetShots()

    try:
        log.info(' ... wait lock ...')
        lock.acquire()
        result = pipeline.Process(shots)
    except Exception:
        log.error("Pipeline processing error ", exc_info=True)
        return 'Error'
    finally:
        lock.release()
        log.info('======= end endpoint /V2/analyse ============================================================================')
    return 'OK' # json.dumps(result[0].Metadata)
    ### FINISH

@app.route('/V1/analyse', methods=['GET'])
def analyseV1():
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

#analyseV2()
