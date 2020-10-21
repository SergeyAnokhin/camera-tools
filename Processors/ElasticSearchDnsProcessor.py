import json, sys
from elasticsearch import Elasticsearch

from Processors.Processor import Processor
from Common.AppSettings import AppSettings

class ElasticSearchDnsProcessor(Processor):
    
    def __init__(self, isSimulation: bool = False):
        super().__init__("ESDNS", isSimulation)
        (self.elasticsearch_host, self.elasticsearch_port) = (None, None)
        if AppSettings.ELASTICSEARCH_HOST:
            (self.elasticsearch_host, self.elasticsearch_port) = AppSettings.ELASTICSEARCH_HOST.split(':')

    def ProcessItem(self, raw, context: dict):
        id = raw['_id']
        index = raw['_index']
        del(raw['_id'])
        del(raw['_index'])
        json_data = json.dumps(raw, indent=4, sort_keys=True)
        self.log.debug(f'➕ Index document: 🆔 ID: {id}  📁 INDEX: {index}')

        try:
            if not self.isSimulation and self.elasticsearch_host:
                es = Elasticsearch(
                    [{'host': self.elasticsearch_host, 'port': self.elasticsearch_port}])
                es.index(index=index, doc_type='_doc', body=json_data, id=id)
            else:
                if self.isSimulation:
                    self.log.debug("Simulation mode. Indexation ignored")
                if not self.elasticsearch_host:
                    self.log.error(
                        "Elasticsearch host not defined. Indexation ignored")
                self.log.debug(json_data)
                meta = self.CreateMetadata(id, context)
                meta['_source'] = raw
        except:
            print("⚠ Unexpected error:", sys.exc_info()[0])
            self.log.debug(json.dumps(raw, indent=4))
            raise
