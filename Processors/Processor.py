import logging
# from Pipeline.Model.PipelineShot import PipelineShot
# from Archiver.CameraArchiveConfig import CameraArchiveConfig
# from Common.CommonHelper import CommonHelper

class Processor:
#     config: CameraArchiveConfig
    isSimulation: bool = False

    def __init__(self, name, isSimulation = False):
        self.name = name
        self.log = logging.getLogger(f"PROC:{name}")
        self.isSimulation = isSimulation

    def Preload(self, isUsed = False):
        ''' Will start on application start once '''
        if isUsed:
            self.log.info('=== PRELOAD ===')

    def Process(self, context: dict):
        ''' Main Process '''
        self.log.info(f'@@@ ⏳ PROCESS: ***{self.name}*** @@@@@@@@@@@@@@@@@@@@@@@@')
        data = context['data']
        for item in data:
            self.BeforeProcessItem(item, context)
            self.ProcessItem(item, context)
        self.AfterProcess(context)

    def CreateMetadata(self, item_id, context: dict):
        if 'meta' not in context:
            context['meta'] = {}    
        if self.name not in context['meta']:
            context['meta'][self.name] = {}
        context['meta'][self.name][item_id] = {}
        return context['meta'][self.name][item_id]

    def ProcessItem(self, item, context):
        pass

    def AfterProcess(self, ctx):
        pass

    def BeforeProcessItem(self, item, ctx):
        pass
