import logging

class Provider:
    isSimulation: bool

    def __init__(self, name, isSimulation: bool):
        self.name = f'PROV:{name}'
        self.log = logging.getLogger(f"PROV:{name}")
        self.isSimulation = isSimulation

    def Get(self, context: dict):
        self.log.info(f'<<<<<< SHOTS: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')
        data = self.GetProtected(context)
        for i in data:
            self.PostProcess(i, context)
        self.log.info(f'<<<<<< SHOTS: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def PostProcess(self, i, context: dict):
        pass

    def GetProtected(self, context):
        return []