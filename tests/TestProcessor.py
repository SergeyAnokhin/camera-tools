from Processors.Processor import Processor

class TestProcessor(Processor):

    def __init__(self, ctx):
        super().__init__("TEST")
        self.Context = ctx

    def AfterProcess(self, pShots: [], ctx: dict):
        ctx.update(self.Context)
