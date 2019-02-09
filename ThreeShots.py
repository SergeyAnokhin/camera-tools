import os
import cv2
from Shot import Shot
from ShotDelta import ShotDelta

class ThreeShots:
    shot1: Shot
    shot2: Shot
    shot3: Shot
    delta12: ShotDelta
    delta23: ShotDelta
    delta31: ShotDelta

    def FromDir(self, dir: str):
        shots = ThreeShots()
        files = os.listdir(dir)

        shots.shot1 = Shot.FromFile(None, os.path.join(dir, files[0]))
        shots.shot2 = Shot.FromFile(None, os.path.join(dir, files[1]))
        shots.shot3 = Shot.FromFile(None, os.path.join(dir, files[2]))

        shots.delta12 = ShotDelta(shots.shot1, shots.shot2)
        shots.delta23 = ShotDelta(shots.shot2, shots.shot3)
        shots.delta31 = ShotDelta(shots.shot3, shots.shot1)

        return shots

    def CalcContours(self):
        self.delta12.CalcCountours()
        self.delta23.CalcCountours()
        self.delta31.CalcCountours()

        for c in self.delta12.Contours:
            (x, y, w, h) = cv2.boundingRect(c)
            rect12 = self.delta12.Threshold[y:(y+h), x:(x+w)]
            rect23 = self.delta23.Threshold[y:(y+h), x:(x+w)]
            rect31 = self.delta31.Threshold[y:(y+h), x:(x+w)]
            max12 = max(rect12)
            max23 = max(rect23)
            max31 = max(rect31)
            pass
