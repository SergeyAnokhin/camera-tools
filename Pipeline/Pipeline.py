import logging

from Processors.Processor import Processor

class Pipeline:
    
    def __init__(self, isSimulation=False):
        self.processors = []
        self.providers = []
        self.log = logging.getLogger(f"PIPE")

    def PreLoad(self):
        for processor in self.processors:
            self.PreLoadProtected(processor)
            PreLoad = getattr(processor, "PreLoad", None)
            if callable(PreLoad):
                processor.PreLoad()

    def PreLoadProtected(self, processor: Processor):
        pass

    def Get(self, context = {}):
        self.log.info(f'~~~~~~~~ PIPELINE START ⏬  GET ~~~~~~~~')
        for provider in self.providers:
            provider.Get(context)
        self.log.info(f'~~~~~~~~ PIPELINE STOP  ⏬  GET ~~~~~~~~')

    def Process(self, context = {}):
        self.log.info(f'~~~~~~~~ PIPELINE START 🛠️ ⚙️ PROCESS ~~~~~~~~')
        for processor in self.processors:
            processor.Process(context)
        self.log.info(f'~~~~~~~~ PIPELINE STOP  🛠️ ⚙️ PROCESS ~~~~~~~~')
