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
import logging, sys, datetime, threading, os, coloredlogs

from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse, HttpRequest
from django.views.generic.base import RedirectView
from django.conf.urls import url, include

from web.ApiContext import ApiContext
from Common.AppSettings import AppSettings
from Providers.ElasticSearchProvider import ElasticSearchProvider

class logit(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        # log_string = self.func.__name__ + " was called"
        # print(log_string)
        # # Open the logfile and append
        # with open(self._logfile, 'a') as opened_file:
        #     # Now we log to the specified logfile
        #     opened_file.write(log_string + '\n')
        # # Now, send a notification
        # self.notify()

        # return base func
        log.info(f'⬛ ⬛ ⬛  ⏩  start endpoint:  /{self.func.__name__} ⬛ ⬛ ⬛ ')
        result = self.func(*args)
        log.info(f'⬛ ⬛ ⬛  ⛔  end endpoint:    /{self.func.__name__} ⬛ ⬛ ⬛ ')
        return result


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_file(path: str, mimetype):
    print(path)
    path = path.replace("\\\\diskstation", "/mnt")
    with open(path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")

### API : /test/ ###
@logit
def test(request):
    return HttpResponse(f"Hello, world. Used settings: {AppSettings.USED_SETTINGS}")

### API : /process/get_dns_data ###
@logit
def processGetDnsData(request):
    return HttpResponse(f"Get Dns Data")

### API : /process/move_mobile_photos ###
@logit
def processMoveMobilePhotos(request):
    return HttpResponse(f"processMoveMobilePhotos")

### API : /camera_archive/archiving ###
@logit
def archiving(request: HttpRequest):
    cameras = request.GET.get("cameras")
    archiveHelper = ApiContext.CameraArchive
    # ['FoscamHut', 'FoscamPTZ', 'Foscam', 'FoscamPlay', 'DLinkCharles', 'DLinkFranck', 'KonxHD']
    configs = archiveHelper.load_configs('configs', cameras.split(','))    
    for config in configs:
        log.info('#################################################')
        files = archiveHelper.get_files(config)
        archiveHelper.move_files(files, config)

    return HttpResponse("Done")

### API : /camera_archive/image ###
@logit
def getImageFromCameraArchive(request: HttpRequest):
    id = request.GET.get('id')
    if not id:
        return ""
    id = ApiContext.Helper.Decode(id)
    isOriginal = True if request.GET.get("original") else False
    (camera, timestamp) = id.split('@')
    time = ApiContext.Helper.FromTimeStampStr(timestamp)

    provider = ElasticSearchProvider(camera, time)
    pShots = provider.GetShots([])
    path = pShots[0].Shot.fullname if not isOriginal else pShots[0].OriginalShot.fullname

    remote_addr = get_client_ip(request)
    log.debug(f'Send file @{remote_addr}: {path} ')
    return send_file(path, mimetype='image/jpeg')

### API : /V3/analyse ###
@logit
def analyseV3(request: HttpRequest):
    ### RUN
    shots = ApiContext.Pipeline.GetShots()

    try:
        log.info(' ... wait lock ...')
        lock.acquire()
        ApiContext.Pipeline.Process(shots)
    except Exception:
        log.error("Pipeline processing error ", exc_info=True)
        return 'Error'
    finally:
        lock.release()
    return HttpResponse("Done") # json.dumps(result[0].Metadata)
    ### FINISH

urlpatterns = [
    path('test/', test),
    path('process/get_dns_data', processGetDnsData),
    path('process/move_mobile_photos', processMoveMobilePhotos),
    path('V3/analyse', analyseV3),
    path('image/', getImageFromCameraArchive),
    path('camera_archive/image', getImageFromCameraArchive),
    path('camera_archive/archiving', archiving),
    path('admin/', admin.site.urls),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    # path('elastic_dsl/', include('web.elastic_dsl.urls')), 
]

ApiContext("TODO")
log = ApiContext.Log
lock = threading.Lock()
