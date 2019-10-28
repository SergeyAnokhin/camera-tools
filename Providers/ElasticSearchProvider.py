import os
from Providers.Provider import Provider
from Common.CommonHelper import CommonHelper
from datetime import datetime
from elasticsearch import Elasticsearch
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.PipelineShot import PipelineShot

class ElasticSearchProvider(Provider):

    def __init__(self, camera: str, datetime: datetime, isSimulation = False):
        super().__init__("ELSE")
        self.camera = camera
        self.datetime = datetime
        self.helper = CommonHelper()
        self.isSimulation = isSimulation
        networkConfig = self.helper.GetNetworkConfig()
        (self.elasticsearch_host, self.elasticsearch_port) = networkConfig['elasticsearch'].split(':')

    def GetShotsProtected(self, pShots: []):
        dtUtc = self.helper.ToUtcTime(self.datetime)
        index = self.helper.GetEsCameraArchiveIndex(dtUtc)
        id = self.helper.GetEsShotId(self.camera, dtUtc)

        if not self.isSimulation:
            es = Elasticsearch([{'host': self.elasticsearch_host, 'port': self.elasticsearch_port}])
            #res = es.get(index="cameraarchive-2019.10", doc_type='doc', id='Foscam@2019-10-20T15:18:08.000Z')
            res = es.get(index=index, doc_type='doc', id=id)
            path_cv = res['_source']['path_cv'] # /CameraArchive/Foscam/2019-10/20/20191020_171808_Foscam_cv.jpeg
            path = res['_source']['path'] # /CameraArchive/Foscam/2019-10/20/20191020_171808_Foscam.jpg
        else:
            path_cv = "/CameraArchive/Foscam/2019-10/20/20191020_171808_Foscam_cv.jpeg"
            path = "/CameraArchive/Foscam/2019-10/20/20191020_171808_Foscam.jpg"

        shot = CamShot(os.path.join("\\\\diskstation", path_cv.lstrip('/').lstrip('\\')))
        pShot = PipelineShot(shot)
        pShot.OriginalShot = CamShot(os.path.join("\\\\diskstation", path.lstrip('/').lstrip('\\')))
        meta = self.CreateMetadata(pShot)
        meta['id'] = id
        meta['index'] = index

        return [pShot]