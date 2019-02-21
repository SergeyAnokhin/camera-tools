# install opencv 4.0.0 : pip install opencv-contrib-python 
import cv2
import time
import os
import logging
import numpy as np
from OpenCV.Shot import Shot
from OpenCV.AnalyseResult import ImageAnalyseResult, ObjectAnalyseResult

class YoloResult:

    def __init__(self):
        self.idxs = []
        self.boxes = []
        self.classIDs = []
        self.confidences = []

class YoloContext:
    confidence = 0.4
    threshold = 0.3

    def __init__(self, yoloName: str):
        self.log = logging.getLogger('YOLO')
        # load the COCO class labels our YOLO model was trained on
        labelsPath = os.path.sep.join([yoloName, "names.txt"])
        self.LABELS = open(labelsPath).read().strip().split("\n")

        # initialize a list of colors to represent each possible class label
        np.random.seed(42)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3),
            dtype="uint8")

        # derive the paths to the YOLO weights and model configuration
        self.weightsPath = os.path.sep.join([yoloName, "model.weights"])
        self.configPath = os.path.sep.join([yoloName, "model.cfg"])

        self.log.debug("[INIT] loading weights from disk... : " + self.weightsPath)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        self.log.debug("[INIT] Load took {:.3f} seconds".format(time.time() - start))
        self.log.debug("[INIT] Confidence: %s", self.confidence)
        self.log.debug("[INIT] Threshold: %s", self.threshold)

        # determine only the *output* layer names that we need from YOLO
        self.layers = self.net.getLayerNames()
        self.layers = [self.layers[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def ProcessShot(self, shot: Shot):

        # construct a blob from the input image and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        self.log.debug("start detect objects on: {}".format(shot.filename))
        image = shot.image_color
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(self.layers)
        self.log.debug("detection took {:.3f} seconds".format(time.time() - start))

        shot.YoloResult = self.ProcessLayerOutputs(layerOutputs, image.shape[:2])
        self.drawRegions(shot)
        self.CalcImageAnalyseResult(shot)

    def ProcessLayerOutputs(self, layerOutputs, imageShape):
        (H, W) = imageShape
        # initialize our lists of detected bounding boxes, confidences, and
        # class IDs, respectively
        result = YoloResult()

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.confidence:
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

        return result

    def drawRegions(self, shot: Shot):
        image = shot.image_contours
        yoloResult = shot.YoloResult

        # ensure at least one detection exists
        if len(yoloResult.idxs) == 0:
            return

        # loop over the indexes we are keeping
        for i in yoloResult.idxs.flatten():
            #print('paint triangle')
            # extract the bounding box coordinates
            (x, y) = (yoloResult.boxes[i][0], yoloResult.boxes[i][1])
            (w, h) = (yoloResult.boxes[i][2], yoloResult.boxes[i][3])

            # draw a bounding box rectangle and label on the image
            color = [int(c) for c in self.COLORS[yoloResult.classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            self.log.debug("Found: =={}==: {:.1f}%".format(
                self.LABELS[yoloResult.classIDs[i]], yoloResult.confidences[i]))
            text = "{}: {:.1f}".format(self.LABELS[yoloResult.classIDs[i]], yoloResult.confidences[i])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)

    def CalcImageAnalyseResult(self, shot: Shot):
        # ensure at least one detection exists
        if len(shot.YoloResult.idxs) == 0:
            return

        # loop over the indexes we are keeping
        for i in shot.YoloResult.idxs.flatten():
            (x, y) = (shot.YoloResult.boxes[i][0], shot.YoloResult.boxes[i][1])
            (w, h) = (shot.YoloResult.boxes[i][2], shot.YoloResult.boxes[i][3])

            (center_x, center_y) = (x + w//2,y + h//2)
            
            obj = ObjectAnalyseResult()
            obj.area = w * h
            obj.profile_proportion = h / w
            obj.center_coordinate = [center_x, center_y]
            obj.confidence = shot.YoloResult.confidences[i]
            obj.label = self.LABELS[shot.YoloResult.classIDs[i]]

            shot.imageAnalyseResult.objects.append(obj)
