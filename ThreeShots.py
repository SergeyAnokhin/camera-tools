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
