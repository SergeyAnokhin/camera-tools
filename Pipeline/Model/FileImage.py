import os, pytz, logging, cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec


class FileImage:

    def __init__(self, fullname: str):
        self.fullname = fullname
        self.local = pytz.timezone("Europe/Paris")
        self.filename = os.path.basename(fullname)
        self.dir = os.path.dirname(fullname)
        self.log = logging.getLogger('SHOT')
        self.image = None

    def Exist(self):
        return os.path.isfile(self.fullname)

    def Write(self, content):
        self.log.info('Write content to: ' + self.fullname)
        fp = open(self.fullname, 'wb')
        fp.write(content)
        fp.close()

    def LoadImage(self, image = None):
        self.image = image
        if self.image == None:
            self.image = mpimg.imread(self.fullname)

    def Show(self):
        plt.figure(figsize=(8, 6.025))
        self.gs1 = gridspec.GridSpec(1, 1, left=0, right=1, top=1,
                                     bottom=0, wspace=0, hspace=0)
        self.LoadImage()
        plt.subplot(self.gs1[0])
        plt.axis("off")
        plt.imshow(self.image, interpolation="bilinear")
        plt.margins(0)
        plt.show()
