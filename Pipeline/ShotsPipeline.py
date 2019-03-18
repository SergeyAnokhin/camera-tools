class ShotsPipeline:

    def __init__(self):
        self.processors = []
        self.postProcessors = []
        self.shots = []
        self.analyseResult = {}

    def PreLoad(self):
        for processor in self.processors:
            processor.PreLoad()

    def Process(self):
        for processor in self.processors:
            analyseResult = processor.Process(self.shots)
            self.analyseResult[processor.name] = analyseResult.ToJson()
            processor.Draw(self.shots)

    def PostProcess(self):
        for processor in self.postProcessors:
            processor.Process(self.shots)
