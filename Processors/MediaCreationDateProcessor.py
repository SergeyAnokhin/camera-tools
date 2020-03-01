from Processors.Processor import Processor

class MediaCreationDateProcessor(Processor):

    def __init__(self, isSimulation: bool = False):
        super().__init__("CRED", isSimulation)

    def ProcessItem(self, raw, context: dict):
        id = raw['_id']
        index = raw['_index']