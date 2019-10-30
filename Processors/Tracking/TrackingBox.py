import logging


class TrackingBox:
    point_size = 10

    def __init__(self, box_data):
        self.log = logging.getLogger(f"PROC:TRAC:TBox")
        self.id = 0
        self.image = []
        (self.w, self.h) = box_data['size']
        self.center = box_data['center_coordinate']
        (self.x, self.y) = self.center
        # self.pos_left_top = (self.x - self.box_size // 2, self.y - self.box_size // 2)
        # self.pos_right_bottom = (self.x + self.box_size // 2, self.y + self.box_size // 2)
        (self.point_left_top, self.point_right_bottom) = self.TransformCenterToLimits(self.x, self.y, self.point_size, self.point_size)
        (self.box_left_top, self.box_right_bottom) = self.TransformCenterToLimits(self.x, self.y, self.h, self.w)
        self.pos_text = (self.x, self.y - 5)

    def GetShape(self):
        if len(self.image) == 0:
            return self.PointToStr(0,0)
        return self.PointToStr(len(self.image), len(self.image[0]))

    def ExtractBox(self, image):
        self.log.debug(f"ExtractBox: Box center_coordinate {self.PointToStr(self.x, self.y)} size {self.PointToStr(self.w, self.h)}")
        self.log.debug(f"ExtractBox: Box Y {self.box_left_top[1]}:{self.box_right_bottom[1]} " + \
                                        f"X {self.box_left_top[0]}:{self.box_right_bottom[0]}")
        self.log.debug(f"ExtractBox: Image size {self.GetShape()}")
        result = image[
                self.box_left_top[1]:self.box_right_bottom[1],
                self.box_left_top[0]:self.box_right_bottom[0]]
        self.log.debug(f"ExtractBox: Result size {self.GetShape()}")
        self.image = result

    def PointToStr(self, x, y):
        return f'{x}x{y}'

    def TransformCenterToLimits(self, center_x, center_y, size_height, size_width):
        ''' Transform (Center & Size) => (LeftTop & RightBottom) '''
        pos_left_top = (center_x - size_width // 2, center_y - size_height // 2)
        pos_right_bottom = (center_x + size_width // 2, center_y + size_height // 2)
        return (pos_left_top, pos_right_bottom)
