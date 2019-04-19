import os, pytz, logging, cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from scipy.misc import imsave

class FileImage:
    image: []

    def __init__(self, fullname: str = None):
        self.log = logging.getLogger('IMG')
        self.local = pytz.timezone("Europe/Paris")
        self.UpdateFullName(fullname)

    def UpdateFullName(self, fullname):
        if fullname == None:
            return        
        self.fullname = fullname
        self.filename = os.path.basename(fullname)
        self.dir = os.path.dirname(fullname)
        _, file_extension = os.path.splitext(self.filename)
        self.filenameExtension = file_extension
        self.filenameWithoutExtension = self.filename.replace(self.filenameExtension, '')

    def Exist(self):
        return os.path.isfile(self.fullname)

    def Write(self, content):
        self.log.info('Write content to: ' + self.fullname)
        fp = open(self.fullname, 'wb')
        fp.write(content)
        fp.close()

    def Save(self):
        params = list()
        image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        if self.filenameExtension == 'png':
            imsave(self.fullname,image,params)
        else:
            cv2.imwrite(self.fullname,image,params)

    def SetImage(self, image):
        self.log.info(f"Set image from array: {len(image)}x{len(image[0])}")
        self.image = image

    def LoadImage(self):
        self.log.info(f"Load image from: {self.fullname}")
        #self.image = mpimg.imread(self.fullname)
        self.image = cv2.imread(self.fullname, cv2.IMREAD_UNCHANGED)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)


    def Show(self):
        plt.figure(figsize=(8, 6.025))
        self.gs1 = gridspec.GridSpec(1, 1, left=0, right=1, top=1,
                                     bottom=0, wspace=0, hspace=0)
        if len(self.image) == 0:
            self.LoadImage()
        plt.subplot(self.gs1[0])
        plt.axis("off")
        plt.imshow(self.image, interpolation="bilinear")
        plt.margins(0)
        plt.show()
