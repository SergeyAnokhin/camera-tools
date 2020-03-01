from Common.CommonHelper import CommonHelper
from Providers.Provider import Provider

class FilesWalkerProvider(Provider):

    def __init__(self, root: str = None, ignoreDirs = [], condition = None):
        super().__init__("WALK")
        self.helper = CommonHelper()
        self.root = root
        self.ignoreDirs = ignoreDirs
        self.condition = condition if condition != None else (lambda f: True)

    def GetProtected(self, context):
        files = self.helper.WalkFiles(self.root, self.condition, self.ignoreDirs)
        return files