import cv2, logging, itertools, os, time, cv2
import numpy as np
from Pipeline.Model.CamShot import CamShot
from Pipeline.Model.ProcessingResult import ProcessingResult


class YoloResult:
    pass


class YoloContext:
    pass


class YoloDetection:

    def __init__(self, detection, shot: CamShot):
        self.detection = detection
        self.shot = shot
        (self.ImageHeight, self.ImageWidth) = self.shot.image.shape[:2]

    def GetClassId(self):
        scores = self.detection[5:]
        return np.argmax(scores)

    def GetConfidence(self):
        scores = self.detection[5:]
        classID = np.argmax(scores)
        return scores[classID]

    def GetBoxCoordinates(self):
        # scale the bounding box coordinates back relative to the
        # size of the image, keeping in mind that YOLO actually
        # returns the center (x, y)-coordinates of the bounding
        # box followed by the boxes' width and height
        box = self.detection[0:4] \
                    * np.array([self.ImageWidth, self.ImageHeight, self.ImageWidth, self.ImageHeight])
        (centerX, centerY, width, height) = box.astype("int")

        # use the center (x, y)-coordinates to derive the top and
        # and left corner of the bounding box
        x = int(centerX - (width / 2))
        y = int(centerY - (height / 2))
        return (x, y, int(width), int(height))

class YoloCamShot: 
    detections = []

    def __init__(self, shot: CamShot):
        self.shot = shot.Copy()
        self.log = logging.getLogger(f"PROC:YOLO:{self.shot.filename}")
        self.boxes = []

    def Detect(self, net, layers):
        #self.log.debug("start detect objects on: {}".format(self.shot.filename))
        blob = cv2.dnn.blobFromImage(self.shot.image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        start = time.time()
        layerOutputs = net.forward(layers)
        self.log.debug("detection took {:.3f} seconds".format(time.time() - start))
        return layerOutputs

    def ProcessOutput(self, layerOutputs, minConfidence, threshold):
        detections = [YoloDetection(d, self.shot) for d in itertools.chain(*layerOutputs)]
        self.detections = [d for d in detections if d.GetConfidence() > minConfidence]

        self.boxes = [d.GetBoxCoordinates() for d in self.detections]
        self.confidences = [d.GetConfidence() for d in self.detections]
        self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, minConfidence, threshold)

    def Draw(self, colors, labels):
        if len(self.idxs) == 0:
            return
        classIDs = [d.GetClassId() for d in self.detections]

        # loop over the indexes we are keeping
        for i in self.idxs.flatten():
            (x, y) = (self.boxes[i][0], self.boxes[i][1])
            (w, h) = (self.boxes[i][2], self.boxes[i][3])
            color = [int(c) for c in colors[classIDs[i]]]
            text = "{}: {:.1f}".format(labels[classIDs[i]], self.confidences[i])

            cv2.rectangle(self.shot.image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(self.shot.image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)

    def GetProcessResult(self, labels):
        # ensure at least one detection exists
        if len(self.idxs) == 0:
            return

        results = []
        classIDs = [d.GetClassId() for d in self.detections]
        for i in self.idxs.flatten():
            result = {}
            (x, y) = (self.boxes[i][0], self.boxes[i][1])
            (w, h) = (self.boxes[i][2], self.boxes[i][3])

            (center_x, center_y) = (x + w//2,y + h//2)
            
            result['area'] = w * h
            result['profile_proportion'] = round(h / w, 2)
            result['center_coordinate'] = [center_x, center_y]
            result['confidence'] = round(self.confidences[i], 2)
            result['label'] = labels[classIDs[i]]
            self.log.info(obj)

            shot.imageAnalyseResult.objects.append(obj)

        return results
    
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

        labelsPath = os.path.sep.join([self.yoloPath, "names.txt"])
        self.LABELS = open(labelsPath).read().strip().split("\n")
        np.random.seed(42)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3), dtype="uint8")
        self.weightsPath = os.path.sep.join([self.yoloPath, "model.weights"])
        self.configPath = os.path.sep.join([self.yoloPath, "model.cfg"])

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
            layerOutputs = yolo.Detect(self.net, self.layers)
            yolo.ProcessOutput(layerOutputs, self.confidence, self.threshold)

        return self.Result

