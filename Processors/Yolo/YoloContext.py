import logging, os, cv2, time
import numpy as np


class YoloContext:
    
    def __init__(self, yoloPath):
        self.log = logging.getLogger("PROC:YOLO:CONTEXT")
        self.isPreLoaded = False
        self.yoloPath = yoloPath

    def PreLoad(self):
        if self.isPreLoaded:
            return

        labelsPath = os.path.sep.join([self.yoloPath, "names.txt"])
        with open(labelsPath) as file:
            self.LABELS = file.read().strip().split("\n")
        np.random.seed(42)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3), dtype="uint8")
        self.weightsPath = os.path.sep.join([self.yoloPath, "model.weights"])
        self.configPath = os.path.sep.join([self.yoloPath, "model.cfg"])

        self.log.debug("[LOAD] loading weights from disk... : " + self.weightsPath)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        self.log.debug("[LOAD] Load took {:.3f} seconds".format(time.time() - start))

        # determine only the *output* layer names that we need from YOLO
        self.layers = self.net.getLayerNames()
        self.layers = [self.layers[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        self.isPreLoaded = True
