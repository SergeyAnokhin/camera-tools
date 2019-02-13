import cv2
import time
import os
import numpy as np
import Shot

class YoloResult:

    def __init__(self):
        self.idxs = []
        self.boxes = []
        self.classIDs = []
        self.confidences = []

class YoloContext:
    confidence = 0.5
    threshold = 0.3

    def __init__(self, yoloName: str):
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

        print("[YOLO] loading weights from disk... : ", self.weightsPath)
        start = time.time()
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        print("[YOLO] Load took {:.3f} seconds".format(time.time() - start))

        # determine only the *output* layer names that we need from YOLO
        self.layers = self.net.getLayerNames()
        self.layers = [self.layers[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def ProcessImage(self, shot: Shot):

        # construct a blob from the input image and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        image = shot.image_color
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        print("[YOLO] start detect objects on: {}".format(shot.filename))
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(self.layers)
        print("[YOLO] detection took {:.3f} seconds".format(time.time() - start))

        return self.ProcessLayerOutputs(layerOutputs, image.shape[:2])

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

    def drawRegions(self, image, yoloResult: YoloResult):
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
            text = "{}: {:.4f}".format(self.LABELS[yoloResult.classIDs[i]], yoloResult.confidences[i])
            print("[YOLO] Found: ", text)
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)
