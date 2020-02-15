import logging, unittest, sys, datetime, os, json
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.test")
from Common.CommonHelper import CommonHelper
from Pipeline.Pipeline import Pipeline
from Providers.DnsAdGuardProvider import DnsAdGuardProvider
from Processors.ElasticSearchDnsProcessor import ElasticSearchDnsProcessor

# from Common.AppSettings import AppSettings

class TestDns(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDns, self).__init__(*args, **kwargs)
        file_handler = logging.FileHandler(filename='test.log', mode='w', encoding='utf-8')
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
            level=logging.DEBUG, 
            datefmt='%H:%M:%S',
            handlers=handlers)
        self.log = logging.getLogger("TEST")
        TestDns.log = self.log

        self.helper = CommonHelper()

        self.helper.installColoredLog(self.log)
        self.log.info(f'start {__name__}: ⏱️ {datetime.datetime.now()}')

    def setUp(self):
        self.log.info(f'⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ')
        self.log.info(f'⬛ ⬛ ⬛  ⏩  SETUP   ⏩   {self._testMethodName} ⬛ ⬛ ⬛ ')

    def tearDown(self):
        self.log.info(f'⬛ ⬛ ⬛  ⛔  TEARDOWN ⛔  {self._testMethodName} ⬛ ⬛ ⬛ ')

    @classmethod
    def tearDownClass(self):
        pass
        # TestPipeline.log.info(' ############################ ')
        # TestPipeline.log.info(' ### TEARDOWN ############### ')
        # TestPipeline.log.info(' ############################ ')

    def test_provider(self):
        # python -m unittest tests.test_dns.TestDns.test_provider
        pipeline = Pipeline(self.log)
        pipeline.providers.append(DnsAdGuardProvider())

        context = {}
        pipeline.Get(context)
        data = context['data']

        self.assertEqual(len(data), 6)
        self.assertEqual(data[5]['client'], '192.168.1.12')
        self.assertEqual(data[5]['elapsedMs'], 12.18)
        self.assertEqual(data[5]['@timestamp'], '2020-02-14T23:17:05.783Z')
        self.assertEqual(data[5]['_id'], 'dns-2020.02')
        self.assertEqual(data[5]['_index'], '192.168.1.12@2020-02-14T23:17:05.783Z_m23.cloudmqtt.com')

    def test_processor(self):
        # python -m unittest tests.test_dns.TestDns.test_processor
        provider_output = """
{
    "answer": [
        {
            "ttl": 300,
            "type": "CNAME",
            "value": "ec2-54-76-137-235.eu-west-1.compute.amazonaws.com."
        }
    ],
    "client": "192.168.1.12",
    "elapsedMs": 12.18,
    "question": {
        "class": "IN",
        "host": "m23.cloudmqtt.com",
        "type": "AAAA"
    },
    "reason": "NotFilteredNotFound",
    "status": "NOERROR",
    "id": 12,
    "client_ip": "192.168.1.12",
    "@timestamp": "2020-02-14T23:17:05.783Z",
    "tags": [
        "camera_tools"
    ],
    "_id": "dns-2020.02",
    "_index": "192.168.1.12@2020-02-14T23:17:05.783Z_m23.cloudmqtt.com"
}        
        """
        pipeline = Pipeline(self.log)
        pipeline.processors.append(ElasticSearchDnsProcessor())

        context = {
            "data": [json.loads(provider_output)]
        }
        pipeline.Process(context)

