import json, logging
from Processors.PipelineShotProcessor import PipelineShotProcessor
from Pipeline.Model.PipelineShot import PipelineShot
from Common.FileInfo import FileInfo
from elasticsearch import Elasticsearch
from Common.AppSettings import AppSettings

class ElasticSearchProcessor(PipelineShotProcessor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("ELSE")
        self.isSimulation = isSimulation
        # for _ in ("boto", "elasticsearch", "urllib3"):
        #     logging.getLogger(_).setLevel(logging.INFO)
        (self.elasticsearch_host, self.elasticsearch_port) = AppSettings.ELASTICSEARCH_HOST.split(':')

    def GetArchivePath(self, path: str):
        path = path.replace("\\\\diskstation", '').replace('\\', '/')
        path = path.replace("/mnt", "")
        return path

    def ProcessItem(self, pShot: PipelineShot, context: dict):
        meta = self.CreateMetadata(pShot)
        #fullfilename_ftp = file.to.path.replace("\\\\diskstation", '').replace('\\', '/')
        file = FileInfo(pShot.Shot.fullname)
        path = self.GetArchivePath(pShot.Metadata['ARCH']['archive_destination_orig'])
        path_cv = self.GetArchivePath(pShot.Metadata['ARCH']['archive_destination'])
        if 'PROV:IMAP' in pShot.Metadata and 'start' in pShot.Metadata['PROV:IMAP']:
            source_type = 'mail'
            event_start = pShot.Metadata['PROV:IMAP']['start']
        elif 'PROV:DIRC' in pShot.Metadata and 'start' in pShot.Metadata['PROV:DIRC']:
            source_type = 'file'
            event_start = pShot.Metadata['PROV:DIRC']['start']
        else:
            source_type = 'unknown'
            event_start = None

        raw = {
            "ext": file.get_extension(),  # 'jpg'
            "volume": "/volume2",
            # "/CameraArchive/Foscam/2019-02/06/20190206_090254_Foscam.jpg",
            "path": path,
            # "/CameraArchive/Foscam/2019-02/06/20190206_090254_Foscam_cv.jpeg",
            "path_cv": path_cv,
            "@timestamp": file.get_timestamp_utc(),  # "2019-02-01T11:40:05.000Z",
            "doc": "event",
            "sensor": self.config.sensor,
            "position": self.config.position,
            "camera": self.config.camera,
            "value": file.size(),
            "source_type": source_type,
            "event_start": event_start,
            "tags": [
                "synology_cameraarchive",
                "camera_tools"
            ]
        }

        raw['Analyse'] = {}
        for metaKey in pShot.Metadata:
            if metaKey == self.name:
                continue
            raw['Analyse'][metaKey] = pShot.Metadata[metaKey]

        json_data = json.dumps(raw, indent=4, sort_keys=True)
        meta['JSON'] = json_data
        meta['timestamp_utc'] = file.get_timestamp_utc()
        id = self.helper.GetEsShotId(self.config.camera, file.get_datetime_utc())
        index = self.helper.GetEsCameraArchiveIndex(file.get_datetime_utc())
        self.log.info(f'- add document: ID = {id} @ Index = {index}')
        self.log.info(f'    - path:    {path}')
        self.log.info(f'    - path_cv: {path_cv}')
        if not self.isSimulation and self.elasticsearch_host:
            es = Elasticsearch([{'host': self.elasticsearch_host, 'port': self.elasticsearch_port}])
            es.index(index=index, doc_type='doc', body=json_data, id=id)
        else:
            if self.isSimulation:
                self.log.debug("Simulation mode. Indexation ignored")
            if not self.elasticsearch_host:
                self.log.debug("Elasticsearch host not defined. Indexation ignored")
            self.log.debug(json_data)
            meta["_index"] = index 
            meta["_id"] = id

