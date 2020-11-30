import logging, unittest, sys, datetime, os, json
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.test")
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.dev_at_home")
from Common.CommonHelper import CommonHelper
from Pipeline.Pipeline import Pipeline
from Providers.DnsAdGuardProvider import DnsAdGuardProvider
from Processors.ElasticSearchDnsProcessor import ElasticSearchDnsProcessor
from tests.TestHelper import TestHelper

# from Common.AppSettings import AppSettings

class TestDns(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDns, self).__init__(*args, **kwargs)
        self.testHelper = TestHelper()
        self.log = self.testHelper.CreateLog(TestDns.__name__)

    def setUp(self):
        self.testHelper.setUp(self.log, self._testMethodName)

    def tearDown(self):
        self.testHelper.tearDown(self.log, self._testMethodName)

    def test_provider(self):
        # python -m unittest tests.test_dns.TestDns.test_provider
        pipeline = Pipeline(self.log)
        pipeline.providers.append(DnsAdGuardProvider(isSimulation=True))

        context = {}
        pipeline.Get(context)
        data = context['items']

        self.assertEqual(len(data), 7)
        self.assertEqual(data[5]['client'], '192.168.1.12')
        self.assertEqual(data[5]['client_id'], 12)
        self.assertEqual(data[5]['elapsedMs'], 12.18)
        self.assertEqual(data[5]['@timestamp'], '2020-02-14T23:17:05.783Z')
        self.assertEqual(data[5]['_index'], 'dns-2020.02')
        self.assertEqual(data[5]['_id'], '192.168.1.12@2020-02-14T23:17:05.783Z_m23.cloudmqtt.com')
        # complex answer check : 
        self.assertEqual(data[6]['answer'][0]['value'], '124.202.138.29')
        self.assertEqual(data[6]['answer'][1]['value'], '175.25.50.70')

    def test_processor(self):
        # python -m unittest tests.test_dns.TestDns.test_processor
        provider_output = json.loads("""
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
    "client_id": 12,
    "client_ip": "192.168.1.12",
    "@timestamp": "2020-02-14T23:17:05.783Z",
    "tags": [
        "camera_tools"
    ],
    "_index": "dns-2020.02",
    "_id": "192.168.1.12@2020-02-14T23:17:05.783Z_m23.cloudmqtt.com"
}        
        """)
        pipeline = Pipeline(self.log)
        pipeline.processors.append(ElasticSearchDnsProcessor(isSimulation=True))

        context = {
            "items": [provider_output]
        }
        pipeline.Process(context)

        meta = context['meta']['ESDNS']["192.168.1.12@2020-02-14T23:17:05.783Z_m23.cloudmqtt.com"]
        generated = meta['_source']

        expected = json.loads("""
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
    "client_id": 12,
    "client_ip": "192.168.1.12",
    "@timestamp": "2020-02-14T23:17:05.783Z",
    "tags": [
        "camera_tools"
    ]
}
        """)

        self.assertEqual(generated['@timestamp'], expected['@timestamp'])
        self.assertDictEqual(generated, expected)

    def test_datetime(self):
        # python -m unittest tests.test_dns.TestDns.test_datetime
        target = DnsAdGuardProvider(isSimulation=True) 

        ## Standard
        # AdGuard:   14:24   14:24:48 30/11/2020 
        # API:       15:24   2020-11-30T15:24:48.684883963+02:00
        # ES Source: 13:24   2020-11-30T13:24:48.684Z
        # Kiabana:   14:24   30/11 14:24:48
        strDt = "2020-11-30T15:24:48.684883963+02:00"
        dt = target.ParseDateTime(strDt)
        expected = datetime.datetime(2020, 11, 30, 15, 24, 48, 684884, 
                            tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        self.assertEqual(dt.hour, expected.hour)
        self.assertEqual(dt.microsecond, expected.microsecond)
        self.assertEqual(dt.tzinfo, expected.tzinfo)
        self.assertEqual(dt, expected)

        # Short microseconds
        strDt = "2020-11-30T02:04:02.07754+02:00"
        dt = target.ParseDateTime(strDt)
        expected = datetime.datetime(2020, 11, 30, 2, 4, 2, 77540, 
                            tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        self.assertEqual(dt, expected)

        # Short microseconds
        strDt = "2020-10-26T00:29:40.88814+01:00"
        target = DnsAdGuardProvider(isSimulation=True) 
        dt = target.ParseDateTime(strDt)
        expected = datetime.datetime(2020, 10, 26, 0, 29, 40, 888140, 
                            tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
        self.assertEqual(dt, expected)


    # def test_real(self):
    #     # python -m unittest tests.test_dns.TestDns.test_real

    #     pipeline = Pipeline(self.log)
    #     pipeline.providers.append(DnsAdGuardProvider())
    #     pipeline.processors.append(ElasticSearchDnsProcessor()) # isSimulation=True

    #     context = {}
    #     pipeline.Get(context)
    #     pipeline.Process(context)

    # def test_dns_resolve_reverse(self):
    #     # python -m unittest tests.test_dns.TestDns.test_dns_resolve_reverse
    #     from dns import reversename, resolver
    #     resolver.default_resolver = resolver.Resolver(configure=False)
    #     resolver.default_resolver.nameservers = ['192.168.1.1'] # AppSettings.DNS_HOST
    #     rev_name = reversename.from_address("192.168.1.16")
    #     answer = resolver.query(rev_name,"PTR", lifetime=60, raise_on_no_answer=False)
    #     print(answer)
    #     print(answer[0].target.labels[0].decode("utf-8"))
