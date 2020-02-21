import os, logging, cv2, shutil
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
#from scipy.misc import imsave # cannot install in docker

class FileImage:

    def __init__(self, fullname: str = None):
        self.log = logging.getLogger('IMAG')
        # self.local = pytz.timezone("Europe/Paris")
        self.image = []
        self.UpdateFullName(fullname)

    def UpdateFullName(self, fullname):
        if fullname == None:
            return       
        self.EnsureImage() 
        self.fullname = fullname
        self.filename = os.path.basename(fullname)
        self.dir = os.path.dirname(fullname)
        _, file_extension = os.path.splitext(self.filename)
        self.filenameExtension = file_extension
        self.filenameWithoutExtension = self.filename.replace(self.filenameExtension, '')

    def Exist(self):
        return os.path.isfile(self.fullname)

    def Write(self, content):
        self.log.info(f'Write brut content to: => {self.fullname}')
        fp = open(self.fullname, 'wb')
        fp.write(content)
        fp.close()

    def Save(self, fullname: str = None):
        params = list()
        self.EnsureImage()
        if fullname:
            self.UpdateFullName(fullname)
        image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        self.log.info(f"Save image: => {self.fullname}")
        # if self.filenameExtension == 'png':
        #     imsave(self.fullname,image,params)
        # else:
        cv2.imwrite(self.fullname,image,params)

    def SetImage(self, image):
        self.log.info(f"Set image from array: {len(image)}x{len(image[0])}")
        self.image = image

    def LoadImage(self):
        self.log.info(f"Load image from: <= {self.fullname}")
        #self.image = mpimg.imread(self.fullname)
        self.image = cv2.imread(self.fullname, cv2.IMREAD_UNCHANGED)
        #self.log.info(f"Image: {len(self.image)}")
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

    def EnsureImage(self):
        if len(self.image) == 0 and hasattr(self, 'fullname') and self.fullname:
            self.LoadImage()

    def GetImage(self):
        self.EnsureImage()
        return self.image

    def Show(self, title_add = ""):
        plt.figure(figsize=(8, 6.025))
        self.gs1 = gridspec.GridSpec(1, 1, left=0, right=1, top=1,
                                     bottom=0, wspace=0, hspace=0)
        fig = plt.gcf()
        fig.canvas.set_window_title(self.filename + title_add)

        self.EnsureImage()
        plt.subplot(self.gs1[0])
        plt.axis("off")
        plt.imshow(self.image, interpolation="bilinear")
        plt.margins(0)


        plt.show()

    # def Move(self, dest: str):
    #     self.log.info(f"Move: {self.fullname} => {dest}")
    #     os.rename(self.fullname, dest)
    #     self.UpdateFullName(dest)
        
    def Move2(self, dest: str):
        if self.Exist():
            orig = self.fullname
            self.log.info(f"Move2: {self.fullname} => {dest}")
            shutil.copy2(self.fullname, dest)
            self.UpdateFullName(dest)
            os.remove(orig)
        elif len(self.image) != 0:
            self.UpdateFullName(dest)
            self.Save()
        
