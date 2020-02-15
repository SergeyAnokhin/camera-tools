import logging, unittest, sys, datetime, requests, re, os
from Common.CommonHelper import CommonHelper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.production")
from Common.AppSettings import AppSettings

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

        helper = CommonHelper()

        helper.installColoredLog(self.log)
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

    def test_basic(self):
        # python -m unittest tests.test_dns.TestDns.test_basic
        url = AppSettings.DNS_ADGUARD.API_QUERY_LOG

        headers = {
            'Authorization': AppSettings.DNS_ADGUARD.API_AUTH,
            'User-Agent': "PostmanRuntime/7.20.1",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }

        response = requests.request("GET", url, headers=headers)
        json = response.json()

        data = json['data']
        oldestMinutes = self.OldestDateTimeMinutes(json['oldest'])
        if oldestMinutes > 20:
            self.log.debug(f'Oldest (minutes): {oldestMinutes} (⏱️ {json["oldest"]})')
        else:
            self.log.error(f'Oldest (minutes): {oldestMinutes} (⏱️ {json["oldest"]})')
        self.log.debug(f"Data symbols : {len(response.text)}")
        self.log.debug(f"Data (items) : {len(data)}")

        for item in data:
            self.log.debug(f"- {item['client']} / {item['question']['host']} / {item['reason']} ")

    def OldestDateTimeMinutes(self, oldestStr: str):
        pattern = re.compile("\.(\d{6})\d+(\D)")
        oldest = pattern.sub(r".\1\2", oldestStr)
        dt = datetime.datetime.fromisoformat(oldest)
        dt = dt.replace(tzinfo=None)
        now = datetime.datetime.now()
        return (now - dt).total_seconds() / 60

    def test_basic2(self):
        # python -m unittest tests.test_dns.TestDns.test_basic2
        pass

