import logging, sys, threading, datetime, locale, coloredlogs, time, os

from Pipeline.ShotsPipeline import ShotsPipeline
from Pipeline.Pipeline import Pipeline

from Providers.DirectoryShotsProvider import DirectoryShotsProvider
from Providers.ImapShotsProvider import ImapShotsProvider
from Providers.ElasticSearchProvider import ElasticSearchProvider
from Providers.DnsAdGuardProvider import DnsAdGuardProvider
from Providers.FilesWalkerProvider import FilesWalkerProvider

from Processors.DiffContoursProcessor import DiffContoursProcessor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Processors.TrackingProcessor import TrackingProcessor
from Processors.ArchiveProcessor import ArchiveProcessor
from Processors.SaveToTempProcessor import SaveToTempProcessor
from Processors.MailSenderProcessor import MailSenderProcessor
from Processors.HassioProcessor import HassioProcessor
from Processors.ElasticSearchProcessor import ElasticSearchProcessor
from Processors.ElasticSearchDnsProcessor import ElasticSearchDnsProcessor
from Processors.MediaCreationDateProcessor import MediaCreationDateProcessor
from Processors.PhotosArrangeProcessor import PhotosArrangeProcessor

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
    ShotsPipeline: ShotsPipeline

    def __init__(self, arg):
        if not ApiContext.IsInitialized:
            self.InitPrivate()
            ApiContext.IsInitialized = True
        # if not ApiContext.Instance:
        #     ApiContext.Instance = ApiContext.ApiContextInstance("TODO")
        # else:
        #     ApiContext.Instance.val = arg

    def InitPrivate(self):

        file_error_handler = logging.FileHandler(filename='logs/camera-tools-error.log', encoding='utf-8')
        file_error_handler.setLevel(logging.ERROR)
        file_handler = logging.handlers.TimedRotatingFileHandler('logs/camera-tools.log', when='midnight',
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
        self.Helper.installColoredLog(self.log)

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
        self.shotsPipeline = ShotsPipeline(self.camera, self.log)
        self.InitShotsPipeline()
        ApiContext.ShotsPipeline = self.shotsPipeline

        self.InitDnsPipeline()
        ApiContext.DnsPipeline = self.dnsPipeline

        self.InitPhotosPipeline()
        ApiContext.PhotosSergeyPipeline = self.photosSergeyPipeline
        ApiContext.PhotosLiliaPipeline = self.photosLiliaPipeline

        self.log.info(f'initialization API finished @ {datetime.datetime.now()}')

    def InitPhotosPipeline(self):
        self.photosSergeyPipeline = Pipeline()
        self.photosSergeyPipeline.providers.append(FilesWalkerProvider("../camera-OpenCV-data/Mobile", ['Lilia']))
        self.photosSergeyPipeline.processors.append(MediaCreationDateProcessor())
        self.photosSergeyPipeline.processors.append(PhotosArrangeProcessor('Mobile Sergey'))

        self.photosLiliaPipeline = Pipeline()
        self.photosLiliaPipeline.providers.append(FilesWalkerProvider("../camera-OpenCV-data/Mobile/Lilia"))
        self.photosLiliaPipeline.processors.append(MediaCreationDateProcessor())
        self.photosLiliaPipeline.processors.append(PhotosArrangeProcessor('Mobile Lilia'))

    def InitShotsPipeline(self):
        self.shotsPipeline.providers.clear()
        self.shotsPipeline.processors.clear()
        self.shotsPipeline.providers.append(ImapShotsProvider())
        self.shotsPipeline.providers.append(DirectoryShotsProvider())
        self.shotsPipeline.processors.append(DiffContoursProcessor())
        self.shotsPipeline.processors.append(YoloObjDetectionProcessor())
        self.shotsPipeline.processors.append(TrackingProcessor())
        self.shotsPipeline.processors.append(SaveToTempProcessor())           
        self.shotsPipeline.processors.append(MailSenderProcessor())
        self.shotsPipeline.processors.append(HassioProcessor('temp' if self.isSimulation else None))        
        self.shotsPipeline.processors.append(ArchiveProcessor(self.isSimulation))
        self.shotsPipeline.processors.append(ElasticSearchProcessor(self.isSimulation)) 
        self.shotsPipeline.PreLoad()

    def InitDnsPipeline(self):
        self.dnsPipeline = Pipeline(self.log)
        self.dnsPipeline.providers.append(DnsAdGuardProvider())
        self.dnsPipeline.processors.append(ElasticSearchDnsProcessor())

