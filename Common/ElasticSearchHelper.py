import json
from elasticsearch import Elasticsearch
from Common.FileInfo import FileInfo

class ElasticSearchHelper:

    def report_to_elastic(self, file: FileInfo):
        config = file.config
        fullfilename_ftp = file.to.path.replace("\\\\diskstation", '').replace('\\', '/')

        dict = {
            "ext": file.to.get_extension(),  # 'jpg'
            "volume": "/volume2",
            # "/Camera/Foscam/FI9805W_C4D6553DECE1/snap/MDAlarm_20190201-124005.jpg",
            "path": fullfilename_ftp,
            "@timestamp": file.to.get_timestamp_utc(),  # "2019-02-01T11:40:05.000Z",
            "doc": "event",
            "sensor": config.sensor,
            "position": config.position,
            "camera": config.camera,
            "value": file.to.size(),
            "tags": [
                "synology_cameraarchive",
                "python_camera_archiver"
            ]
        }
        json_data = json.dumps(dict, indent=4, sort_keys=True)
        #print('{}@{}'.format(config.camera, file.to.get_timestamp_utc()), json_data)
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res = es.index(index="cameraarchive-" + file.to.get_month_id_utc(),
                       doc_type='doc',
                       body=json_data,
                       id='{}@{}'.format(config.camera, file.to.get_timestamp_utc()))
