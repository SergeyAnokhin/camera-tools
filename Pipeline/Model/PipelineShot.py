from Pipeline.Model.CamShot import CamShot

class PipelineShot:
    def __init__(self, shot: CamShot, index = 0):
        self.Shot = shot # image for draw
        self.OriginalShot = shot.Clone() # image read only
        self.Metadata = {} # put analyse result metadata by processor
        self.Index = index
        self.Id = shot.filename
