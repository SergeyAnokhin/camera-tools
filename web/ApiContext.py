import logging, sys, threading, datetime, locale, coloredlogs, time, os

from Pipeline.ShotsPipeline import ShotsPipeline
from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Providers.ImapShotsProvider import ImapShotsProvider
from Providers.ElasticSearchProvider import ElasticSearchProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Processors.HassioProcessor import HassioProcessor
from Processors.ElasticSearchProcessor import ElasticSearchProcessor

from Common.SecretConfig import SecretConfig
from Common.CommonHelper import CommonHelper
from Common.ElasticSearchHelper import ElasticSearchHelper
from Common.AppSettings import AppSettings
from Common import HtmlLogger

from Archiver.CameraArchiveHelper import CameraArchiveHelper

class ApiContext:
    # class ApiContextInstance:
    #     def __init__(self, arg):
    #         self.val = arg
    # Instance = None
    IsInitialized = False
    Log = None
    Helper = CommonHelper()
    CameraArchive: CameraArchiveHelper
    ElasticSearch: ElasticSearchHelper
    Pipeline: ShotsPipeline

    def __init__(self, arg):
        if not ApiContext.IsInitialized:
            self.InitPrivate()
            ApiContext.IsInitialized = True
        # if not ApiContext.Instance:
        #     ApiContext.Instance = ApiContext.ApiContextInstance("TODO")
        # else:
        #     ApiContext.Instance.val = arg

    def InitPrivate(self):

        file_error_handler = logging.FileHandler(filename='camera-tools-error.log', encoding='utf-8')
        file_error_handler.setLevel(logging.ERROR)
        file_handler = logging.handlers.TimedRotatingFileHandler('camera-tools.log', when='midnight',
            backupCount=7, encoding='utf-8')
        file_handler.suffix = '_%Y-%m-%d.log'
        # html_handler = HtmlLogger.HTMLRotatingFileHandler('camera-tools.html')
        # html_handler.suffix = '_%Y-%m-%d_%H.html'
        # html_handler.setFormatter(HtmlLogger.HTMLFormatter())
        locale.getpreferredencoding() #need for display emoji in terminal
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler, file_error_handler]

        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
            level=logging.DEBUG, 
            datefmt='%H:%M:%S',
            handlers=handlers)

        self.log = logging.getLogger("API")
        ApiContext.Log = self.log
        self.log.info('ℹ️ |############################################################|')
        self.log.info(f'ℹ️ |####### start API @ {str(datetime.datetime.now()) + " ":#<40}|')
        self.log.info('ℹ️ |############################################################|')
        self.log.info("USED_SETTINGS: " + AppSettings.USED_SETTINGS)


        coloredlogs.DEFAULT_DATE_FORMAT = '%H:%M:%S'
        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {
            'asctime': {'color': 'green'}, 
            'hostname': {'color': 'black'}, 
            'levelname': {'color': 'magenta', 'bold': True, 'underline': True}, 
            'name': {'color': 'blue'}, 
            'programname': {'color': 'cyan'}
        }
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'critical': {'color': 'red', 'bold': True, 'background': 'black'}, 
            'debug': {'color': 1, 'bold': True}, 
            'error': {'color': 'red'}, 
            'info': {'color': 'black', 'faint': True}, 
            'warning': {'color': 'yellow'},
            'notice': {'color': 'magenta'}, 
            'spam': {'color': 'green', 'faint': True}, 
            'success': {'color': 'green', 'bold': True}, 
            'verbose': {'color': 'blue'}, 
        }
        coloredlogs.COLOREDLOGS_LEVEL_STYLES='spam=22;debug=1;verbose=34;notice=220;warning=202;success=118,bold;error=124;critical=background=red'
        coloredlogs.install(logger=self.log, isatty=True)
        coloredlogs.install(level=logging.DEBUG, fmt='%(asctime)s|%(levelname)-.3s|%(name)-.10s: %(message)s', isatty=True)

        # Some examples.
        # self.log.debug("this is a debugging message")
        # self.log.info("this is an informational message")
        # self.log.warning("this is a warning message")
        # self.log.error("this is an error message")
        # self.log.critical("this is a critical message")

        self.isSimulation = False
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()

        ApiContext.CameraArchive = CameraArchiveHelper(self.log)
        ApiContext.ElasticSearch = ElasticSearchHelper()

        self.camera = 'Foscam'
        self.pipeline = ShotsPipeline(self.camera, self.log)
        self.InitPipeline()
        ApiContext.Pipeline = self.pipeline

        self.log.info(f'initialization API finished @ {datetime.datetime.now()}')

    def InitPipeline(self):
        self.pipeline.providers.clear()
        self.pipeline.processors.clear()
        self.pipeline.providers.append(ImapShotsProvider())
        self.pipeline.providers.append(DirectoryShotsProvider())
        self.pipeline.processors.append(DiffContoursProcessor())
        self.pipeline.processors.append(YoloObjDetectionProcessor())
        self.pipeline.processors.append(TrackingProcessor())
        self.pipeline.processors.append(SaveToTempProcessor())           
        self.pipeline.processors.append(MailSenderProcessor())
        self.pipeline.processors.append(HassioProcessor('temp' if self.isSimulation else None))        
        self.pipeline.processors.append(ArchiveProcessor(self.isSimulation))
        self.pipeline.processors.append(ElasticSearchProcessor(self.isSimulation)) 
        self.pipeline.PreLoad()