import unittest, logging, datetime, os, sys
from Common.CommonHelper import CommonHelper

class TestHelper:

    def CreateLog(self, name: str):

        file_error_handler = logging.FileHandler(filename=name + '-test-error.log', encoding='utf-8')
        file_error_handler.setLevel(logging.ERROR)
        file_handler = logging.FileHandler(filename=name + '-test.log', mode='w', encoding='utf-8')
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler, file_error_handler]

        logging.basicConfig(format='%(asctime)s|%(levelname)-.3s|%(name)s: %(message)s', # \t####=> %(filename)s:%(lineno)d 
            level=logging.DEBUG, 
            datefmt='%H:%M:%S',
            handlers=handlers)
        log = logging.getLogger("TEST")

        self.helper = CommonHelper()

        self.helper.installColoredLog(log)
        log.info(f'start {__name__}: ⏱️ {datetime.datetime.now()}')
        return log

    def setUp(self, log: logging.Logger, testMethodName: str):
        log.info(f'⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ')
        log.info(f'⬛ ⬛ ⬛  ⏩  SETUP   ⏩   {testMethodName} ⬛ ⬛ ⬛ ')

    def tearDown(self, log: logging.Logger, testMethodName: str):
        log.info(f'⬛ ⬛ ⬛  ⛔  TEARDOWN ⛔  {testMethodName} ⬛ ⬛ ⬛ ')

    # @classmethod
    # def tearDownClass(self):
    #     pass
    #     # TestPipeline.log.info(' ############################ ')
    #     # TestPipeline.log.info(' ### TEARDOWN ############### ')
    #     # TestPipeline.log.info(' ############################ ')