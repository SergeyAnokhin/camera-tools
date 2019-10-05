import json, logging
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot
from Common.FileInfo import FileInfo
from elasticsearch import Elasticsearch

class ElasticSearchProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("ELSE")
        self.isSimulation = isSimulation
        for _ in ("boto", "elasticsearch", "urllib3"):
            logging.getLogger(_).setLevel(logging.INFO)

    def GetArchivePath(self, path: str):
        path = path.replace("\\\\diskstation", '').replace('\\', '/')
        return path

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)
        #fullfilename_ftp = file.to.path.replace("\\\\diskstation", '').replace('\\', '/')
        file = FileInfo(pShot.Shot.fullname)
        path = self.GetArchivePath(pShot.Metadata['ARCH']['archive_destination_orig'])
        path_cv = self.GetArchivePath(pShot.Metadata['ARCH']['archive_destination'])

        dict = {
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
            "tags": [
                "synology_cameraarchive",
                "camera_tools"
            ]
        }

        dict['Analyse'] = {}
        for metaKey in pShot.Metadata:
            if metaKey == self.name:
                continue
            dict['Analyse'][metaKey] = pShot.Metadata[metaKey]

        json_data = json.dumps(dict, indent=4, sort_keys=True)
        #print('{}@{}'.format(self.config.camera, file.get_timestamp_utc()), json_data)
        meta['JSON'] = json_data
        meta['timestamp_utc'] = file.get_timestamp_utc()
        id = '{}@{}'.format(self.config.camera, file.get_timestamp_utc())
        self.log.info(f'- add document: ID = {id}')
        self.log.info(f'    - path:    {path}')
        self.log.info(f'    - path_cv: {path_cv}')
        if not self.isSimulation:
            es = Elasticsearch([{'host': '192.168.1.31', 'port': 9200}])
            res = es.index(index="cameraarchive-" + file.get_month_id_utc(),
                        doc_type='doc', body=json_data, id=id)
