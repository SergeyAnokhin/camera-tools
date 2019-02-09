import cv2
import matplotlib.pyplot as plt

class Shot:
    filename = ''
    contourArea: int
    image: any
    image_timestamp: any
    Contours = []

    def FromFile(self, path: str):
        self = Shot()
        self.filename = path
        print('Open file: {}'.format(self.filename))
        self.image = cv2.imread(self.filename, cv2.IMREAD_GRAYSCALE)
        self.image_color = cv2.imread(self.filename, cv2.IMREAD_COLOR)
        self.image_contours = self.image_color.copy()
        if len(self.image) == 0:
            raise ValueError('cant load: {}'.format(self.filename))
        self.image_timestamp = self.image[:22, :230]
        self.image[:22, :230] = 0
        
        return self

    def show_cv(self):
        cv2.imshow('shot.show_cv (press any key for close)', self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_plt(self):
        plt.axis("off")
        #plt.title('shot.show_plt')
        img = cv2.cvtColor(self.image_contours, cv2.COLOR_BGR2RGB)
        plt.imshow(img, interpolation="bilinear")

    def DrawContours(self):
        cv2.drawContours(self.image_contours,
                         self.Contours, -1, (0, 255, 255), 1)
        for c in self.Contours[0:2]:
            area = int(cv2.contourArea(c) / 100)
            print('Contour: {}'.format(area))

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(self.image_contours, (x, y),
                          (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(self.image_contours, str(
                area), (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def MagnifyMotion(self):
        if len(self.Contours) == 0:
            return

        counts = 1
        margin = 5
        zoom = 2

        for c in self.Contours[0:counts]:
            (x, y, w, h) = cv2.boundingRect(c)
            img = self.image_color
            motion_area = img[y:(y+h), x:(x+w)]
            img_xmax = len(img[0])
            img_ymax = len(img)
            motion_area = cv2.resize(
                motion_area, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
            y_max = img_ymax-margin
            y_min = y_max - zoom*h
            x_max = img_xmax-margin
            x_min = x_max - zoom*w
            self.image_contours[y_min:y_max, x_min:x_max] = motion_area
            cv2.rectangle(self.image_contours, (x_min, y_min),
                          (x_max, y_max), (127, 127, 127), 2)
