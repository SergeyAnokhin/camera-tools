"""composeexample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging, sys, datetime, threading

from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse, HttpRequest
from django.views.generic.base import RedirectView

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


def test(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def getImageFromCameraArchive(request: HttpRequest):
    id = request.GET.get('id')
    if not id:
        return ""
    id = helper.Decode(id)
    log.info(f'====== start endpoint /image ID: {id} ============================================================================')
    isOriginal = True if request.GET.get("original") else False
    (camera, timestamp) = id.split('@')
    time = helper.FromTimeStampStr(timestamp)

    provider = ElasticSearchProvider(camera, time)
    pShots = provider.GetShots([])
    path = pShots[0].Shot.fullname if not isOriginal else pShots[0].OriginalShot.fullname

    remote_addr = get_client_ip(request)
    log.debug(f'Send file @{remote_addr}: {path} ')
    log.info(f'======= end endpoint /image ID: {id} ============================================================================')
    return send_file(path, mimetype='image/jpeg')

def send_file(path: str, mimetype):
    print(path)
    path = path.replace("\\\\diskstation", "/mnt")
    with open(path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def InitPipeline():
    pipeline.providers.clear()
    pipeline.processors.clear()
    pipeline.providers.append(ImapShotsProvider())
    pipeline.providers.append(DirectoryShotsProvider())
    pipeline.processors.append(DiffContoursProcessor())
    pipeline.processors.append(YoloObjDetectionProcessor())
    pipeline.processors.append(TrackingProcessor())
    pipeline.processors.append(SaveToTempProcessor())           
    pipeline.processors.append(MailSenderProcessor())
    pipeline.processors.append(HassioProcessor('temp' if isSimulation else None))        
    pipeline.processors.append(ArchiveProcessor(isSimulation))
    pipeline.processors.append(ElasticSearchProcessor(isSimulation)) 
    pipeline.PreLoad()

def analyseV2(request: HttpRequest):
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

urlpatterns = [
    path('test/', test),
    path('V2/analyse', analyseV2),
    path('camera_archive/', getImageFromCameraArchive),
    path('admin/', admin.site.urls),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

file_error_handler = logging.FileHandler(filename='camera-tools-error.log')
file_error_handler.setLevel(logging.ERROR)
file_handler = logging.handlers.TimedRotatingFileHandler('camera-tools.log', when='midnight', backupCount=7)
file_handler.suffix = '_%Y-%m-%d.log'
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler, file_error_handler]

logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
    level=logging.DEBUG, 
    datefmt='%H:%M:%S',
    handlers=handlers)

log = logging.getLogger("API")
log.info('|################################################################################|')
log.info('|####### start API @ %s #################################|', datetime.datetime.now())
log.info('|################################################################################|')

isSimulation = False
secretConfig = SecretConfig()
secretConfig.fromJsonFile()
helper = CommonHelper()
lock = threading.Lock()

camera = 'Foscam'
pipeline = ShotsPipeline(camera)
InitPipeline()

log.info('initialization API finished @ %s', datetime.datetime.now())

