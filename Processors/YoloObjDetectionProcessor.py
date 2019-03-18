import cv2, logging, itertools, os, time
import numpy as np
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.ProcessingResult import ProcessingResult


class YoloDetection:

    def __init__(self, detection):
        self.detection = detection

    def GetClassId(self):
        scores = self.detection[5:]
        return np.argmax(scores)

    def GetConfidence(self):
        scores = self.detection[5:]
        classID = np.argmax(scores)
        return scores[classID]


class YoloCamShot: 

    def __init__(self, shot: CamShot):
        self.shot = shot.Copy()

    def Detect(self):
        self.log.debug("start detect objects on: {}".format(self.shot.filename))
        blob = cv2.dnn.blobFromImage(self.shot.image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(self.layers)
        self.log.debug("detection took {:.3f} seconds".format(time.time() - start))
        return layerOutputs

    def ProcessOutput(self, layerOutputs):
        (H, W) = self.shot.image.shape[:2]

        for detection in itertools.chain(*layerOutputs):
            # extract the class ID and confidence (i.e., probability) of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence <= self.confidence:
                continue

            # scale the bounding box coordinates back relative to the
            # size of the image, keeping in mind that YOLO actually
            # returns the center (x, y)-coordinates of the bounding
            # box followed by the boxes' width and height
            box = detection[0:4] * np.array([W, H, W, H])
            (centerX, centerY, width, height) = box.astype("int")

            # use the center (x, y)-coordinates to derive the top and
            # and left corner of the bounding box
            x = int(centerX - (width / 2))
            y = int(centerY - (height / 2))

            # update our list of bounding box coordinates, confidences,
            # and class IDs
            result.boxes.append([x, y, int(width), int(height)])
            result.confidences.append(float(confidence))
            result.classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping bounding
        result.idxs = cv2.dnn.NMSBoxes(result.boxes, result.confidences, self.confidence, self.threshold)

    def Draw(self):
        pass

    def GetProcessResult(self):
        pass
    
class YoloObjDetectionProcessor:
    confidence = 0.4
    threshold = 0.3

    def __init__(self, shot: CamShot, shots):
        self.Result = ProcessingResult()
        self.log = logging.getLogger("PROC:YOLO")
        self.shots = shots
        self.isPreLoaded = False
        self.yoloPath = '..\\camera-OpenCV-data\\weights\\yolo-coco'

    def PreLoad(self):
        if self.isPreLoaded:
            return

        labelsPath = os.path.sep.join([yoloPath, "names.txt"])
        self.LABELS = open(labelsPath).read().strip().split("\n")
        np.random.seed(42)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3), dtype="uint8")
        self.weightsPath = os.path.sep.join([yoloPath, "model.weights"])
        self.configPath = os.path.sep.join([yoloPath, "model.cfg"])

        self.log.debug("[LOAD] loading weights from disk... : " + self.weightsPath)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        self.log.debug("[LOAD] Load took {:.3f} seconds".format(time.time() - start))
        self.log.debug("[LOAD] Confidence: %s", self.confidence)
        self.log.debug("[LOAD] Threshold: %s", self.threshold)

        # determine only the *output* layer names that we need from YOLO
        self.layers = self.net.getLayerNames()
        self.layers = [self.layers[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        self.isPreLoaded = True

    def Process(self):
        for shot in self.shots:
            yolo = YoloCamShot(shot)
            yolo.Detect()

        return self.Result

