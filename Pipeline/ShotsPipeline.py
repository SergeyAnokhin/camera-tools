class ShotsPipeline:

    def __init__(self):
        self.processors = []

    def PreLoad(self):
        for processor in self.processors:
            PreLoad = getattr(processor, "PreLoad", None)
            if callable(PreLoad):
                processor.PreLoad()

    def Process(self, shots: []):
        for processor in self.processors:
            processor.Process(shots)
        return shots

    def Show(self):
        pass
