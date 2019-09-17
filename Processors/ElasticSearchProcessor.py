import json
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot
from Common.FileInfo import FileInfo
from elasticsearch import Elasticsearch

class ElasticSearchProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("ELSE")
        self.isSimulation = isSimulation

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        meta = self.CreateMetadata(pShot)
        #fullfilename_ftp = file.to.path.replace("\\\\diskstation", '').replace('\\', '/')
        file = FileInfo(pShot.Shot.fullname)

        dict = {
            "ext": file.get_extension(),  # 'jpg'
            "volume": "/volume2",
            # "/Camera/Foscam/FI9805W_C4D6553DECE1/snap/MDAlarm_20190201-124005.jpg",
            "path": file.path,
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
        json_data = json.dumps(dict, indent=4, sort_keys=True)
        #print('{}@{}'.format(self.config.camera, file.get_timestamp_utc()), json_data)
        meta['JSON'] = json_data
        meta['timestamp_utc'] = file.get_timestamp_utc()
        if not self.isSimulation:
            es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
            res = es.index(index="cameraarchive-" + file.get_month_id_utc(),
                        doc_type='doc',
                        body=json_data,
                        id='{}@{}'.format(self.config.camera, file.get_timestamp_utc()))
