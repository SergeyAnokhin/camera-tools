import os, pytz, logging


class FileCamShot:

    def __init__(self, fullname: str):
        self.fullname = fullname
        self.local = pytz.timezone("Europe/Paris")
        self.filename = os.path.basename(fullname)
        self.dir = os.path.dirname(fullname)
        self.log = logging.getLogger('SHOT')

    def Exist(self):
        return os.path.isfile(self.fullname)

    def Write(self, content):
        self.log.info('Write content to: ' + self.fullname)
        fp = open(self.fullname, 'wb')
        fp.write(content)
        fp.close()