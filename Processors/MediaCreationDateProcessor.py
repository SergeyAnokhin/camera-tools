from Common.MediaInfo import MediaInfo
from Processors.Processor import Processor

class MediaCreationDateProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("CRED", isSimulation)

    def ProcessItem(self, filename: str, context: dict):
        info = MediaInfo(filename)
        meta = self.CreateMetadata(filename, context)
        meta['shottime'] = info.GetShotTime()