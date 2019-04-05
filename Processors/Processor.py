import logging
from Pipeline.Model.ProcessingResult import ProcessingResult

class ProcessingContext:
    def __init__(self, index: int, shots: []):
        self.Shots = shots
        self.Index = index
        self.Shot = self.Shots[index]
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

    def Process(self, shots):
        ''' Main Process '''
        self.log.info('=== PROCESS ===')
        results = []
        size = len(shots)
        for i in range(size):
            ctx = ProcessingContext(i, shots)
            self.log.debug(f"====== {ctx.Shot.filename} ========================================")
            result = self.ProcessShot(ctx)
            results.append(result)
        return results

    def ProcessShot(self, ctx: ProcessingContext):
        return ProcessingResult()