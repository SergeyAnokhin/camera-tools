import logging
from Pipeline.Model.ProcessingResult import ProcessingResult

class ProcessingContext:
    def __init__(self):
        self.Shots = []
        self.OriginalShots = []

class ShotProcessingContext:
    def __init__(self, index: int, ctx: ProcessingContext):
        self.Index = index

        self.Shots = ctx.Shots
        self.Shot = self.Shots[index]
        self.OriginalShots = ctx.OriginalShots
        self.OriginalShot = self.OriginalShots[index]

        self.OthersShots = self.Shots.copy()
        self.OthersShots.remove(self.Shot)

class Processor:
    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(f"PROC:{name}")
        self.PipelineResults = {}

    def Preload(self, isUsed = False):
        ''' Will start on application start once '''
        if isUsed:
            self.log.info('=== PRELOAD ===')

    def Process(self, ctx: ProcessingContext):
        ''' Main Process '''
        self.log.info('=== PROCESS ===')
        results = []
        for i in range(len(ctx.Shots)):
            ctxShot = ShotProcessingContext(i, ctx)
            self.log.debug(f"====== {ctxShot.Shot.filename} ========================================")
            result = self.ProcessShot(ctxShot)
            results.append(result)
        return results

    def ProcessShot(self, ctx: ShotProcessingContext):
        return ProcessingResult()