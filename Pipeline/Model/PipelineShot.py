from Pipeline.Model.CamShot import CamShot

class PipelineShot:
    def __init__(self, shot: CamShot):
        self.Shot = shot # image for draw
        self.OriginalShot = shot.Copy() # image read only
        self.Metadata = {} # put analyse result metadata by processor