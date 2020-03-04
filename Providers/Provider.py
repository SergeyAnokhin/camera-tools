import logging

class Provider:
    isSimulation: bool

    def __init__(self, name, isSimulation: bool = False):
        self.name = f'PROV:{name}'
        self.log = logging.getLogger(f"PROV:{name}")
        self.isSimulation = isSimulation

    def Get(self, context: dict):
        self.log.info(f'<<<<<< PROVIDER: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')
        items = self.GetProtected(context)
        context['count'] = len(items)
        context['items'] = list(items)
        for i in items:
            self.PostProcess(i, context)
        self.log.info(f'<<<<<< PROVIDER: ***{self.name}*** >>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def PostProcess(self, i, context: dict):
        pass

    def GetProtected(self, context) -> []:
        return []