import os, filetype, logging
from asq import query
from datetime import datetime
from pprint import pprint
import PIL.ExifTags # pip install pillow
# import enzyme
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
# import hachoir
from Common.CommonHelper import CommonHelper

class MediaInfo:

    props = ['datetime_meta_create', 'datetime_meta_modif',  'datetime_name', 
            'datetime_file_create', 'datetime_file_modif']

    def __init__(self, filename = None):
        if not filename:
            return
        self.filename = filename
        self.helper = CommonHelper()
        self.log = logging.getLogger(f"META")

        self.log.info(f'========== {filename} ==========')
        self.ProcessFileName()

        if self.mediatype == 'image':
            self.ProcessImageMeta()
        elif self.mediatype == 'video':
            self.ProcessVideoMeta()

        self.ProcessFileAttributes()

    def ProcessFileAttributes(self):
        stat = os.stat(self.filename)
        self.datetime_file_create = datetime.fromtimestamp(stat.st_ctime)
        self.datetime_file_modif = datetime.fromtimestamp(stat.st_mtime)

    def ProcessVideoMeta(self):
        self.datetime_meta_create = None
        self.datetime_meta_modif = None
        parser = createParser(self.filename)
        if not parser:
            self.log.warning(f"Can't parse file: {self.filename}")
        
        with parser:
            try:
                metadata = extractMetadata(parser)
            except Exception as err:
                self.log.error("Metadata extraction error: %s" % err)
                metadata = None
        if not metadata:
            self.log.error("Unable to extract metadata")
        else:
            dic = metadata.exportDictionary()
            # pprint(dic)
            self.datetime_meta_create = self.helper.get_datetime(dic['Metadata']['Creation date'])
            self.datetime_meta_modif = self.helper.get_datetime(dic['Metadata']['Last modification'])

    def ProcessImageMeta(self):
        self.datetime_meta_create = None
        self.datetime_meta_modif = None

        imgFile = PIL.Image.open(self.filename)
        try:
            exifDict = imgFile._getexif()
        except AttributeError as err:
            self.log.warning(f'Error during extract exif: {err}')
            exifDict = None            
        if exifDict:
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in exifDict.items()
                if k in PIL.ExifTags.TAGS
            }
            # pprint(self.filename)
            # pprint(exif['DateTimeDigitized'])
            self.datetime_meta_create = self.helper.get_datetime(exif['DateTimeDigitized'])
        else:
            self.log.warning(f"No exif data in {self.filename}")

    def ProcessFileName(self):
        self.datetime_name = self.helper.get_datetime(self.filename, False)
        # if dt != None:
        #     self.log.debug(f"{dt:%Y-%m-%d %H:%M:%S} File: {f}")

        kind = filetype.guess(self.filename)
        if kind is None:
            self.log.error(f'Cannot guess file type: {self.filename}')
        else:
            self.mediatype = kind.mime.split('/')[0]
            self.mediaextension = kind.mime.split('/')[1]

    def __str__(self):
        dic = MediaInfo()
        dtShot = self.GetShotTime()
        result = '\n'
        for k in MediaInfo.props:
            if k not in self.__dict__:
                continue
            v = self.__dict__[k]
            if not v:
                continue
            dtStr = self.helper.ToTimeStampStr(v)
            dic.__setattr__(k, dtStr)
            result += f' -- {k: <25}: {dtStr} {"*" if v == dtShot else ""}\n'

        result += f' : {"Shot time": <25}: {dtShot}\n'

        return result # str(vars(dic))

    def GetShotTime(self):
        dates = [self.datetime_meta_create, self.datetime_meta_modif,
                self.datetime_name, self.datetime_file_create,
                self.datetime_file_modif, datetime.now()]
        return query(dates) \
            .where(lambda dt: dt != None) \
            .min()
        

