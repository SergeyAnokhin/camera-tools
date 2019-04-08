from Processors.Processor import ProcessingContext


class ShotsPipeline:

    def __init__(self):
        self.processors = []
        self.postProcessors = []

    def PreLoad(self):
        for processor in self.processors:
            PreLoad = getattr(processor, "PreLoad", None)
            if callable(PreLoad):
                processor.PreLoad()

    def Process(self, shots: []):
        ctx = ProcessingContext()
        ctx.Shots = shots
        ctx.OriginalShots = shots
        analyseResults = {}
        for processor in self.processors:
            processor.PipelineResults = analyseResults
            analyseResult = processor.Process(ctx)
            analyseResults[processor.name] = analyseResult
            ctx.Shots = [r.Shot for r in analyseResult]
        return analyseResults

    def PostProcess(self):
        for processor in self.postProcessors:
            processor.Process(self.shots)

    def Show(self):
        pass
