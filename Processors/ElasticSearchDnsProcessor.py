import json
from elasticsearch import Elasticsearch

from Processors.Processor import Processor
from Common.AppSettings import AppSettings

class ElasticSearchDnsProcessor(Processor):
    
    def __init__(self, isSimulation: bool = False):
        super().__init__("ESDNS", isSimulation)
        (self.elasticsearch_host, self.elasticsearch_port) = AppSettings.ELASTICSEARCH_HOST.split(':')        

    def ProcessItem(self, raw, context: dict):

        json_data = json.dumps(raw, indent=4, sort_keys=True)
        id = raw['_id']
        index = raw['_index']
        del(raw['_id'])
        del(raw['_index'])
        self.log.debug(f'➕ Index document: 🆔 ID: {id}  📁 INDEX: {index}')
        self.log.debug(json.dumps(raw, indent=4))
        if not self.isSimulation and self.elasticsearch_host:
            es = Elasticsearch([{'host': self.elasticsearch_host, 'port': self.elasticsearch_port}])
            es.index(index=index, doc_type='doc', body=json_data, id=id)
        else:
            if self.isSimulation:
                self.log.debug("Simulation mode. Indexation ignored")
            if not self.elasticsearch_host:
                self.log.error("Elasticsearch host not defined. Indexation ignored")
            self.log.debug(json_data)
            meta = self.CreateMetadata(id, context)
            meta['_source'] = raw