import logging
from Pipeline.Model.PipelineShot import PipelineShot

# class ProcessingContext:
#     def __init__(self):
#         self.Shots = []
#         self.OriginalShots = []

# class ShotProcessingContext:
#     def __init__(self, index: int, ctx: ProcessingContext):
#         self.Index = index

#         self.Shots = ctx.Shots
#         self.Shot = self.Shots[index]
#         self.OriginalShots = ctx.OriginalShots
#         self.OriginalShot = self.OriginalShots[index]

#         self.OthersShots = self.Shots.copy()
#         self.OthersShots.remove(self.Shot)

class Processor:
    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(f"PROC:{name}")
        self.PipelineResults = {}

    def Preload(self, isUsed = False):
        ''' Will start on application start once '''
        if isUsed:
            self.log.info('=== PRELOAD ===')

    def Process(self, pShots: []):
        ''' Main Process '''
        self.log.info('=== PROCESS ===')
        for i in range(len(pShots)):
            pShot = pShots[i]
            otherPShots = pShots.copy()
            otherPShots.remove(pShot)
            self.log.debug(f"====== {pShot.Shot.filename} ========================================")
            self.ProcessShot(pShot, otherPShots)

    def ProcessShot(self, pShot: PipelineShot, otherPShots: []):
        pass