import ulab as ul
from .kalmanfilter import *
from .schmitttrigger import *

def sqeuclidean(a, b):
    if a.shape == (1,2):
        a.transpose()
    if b.shape == (1,2):
        b.transpose()

    return (b[0][0] - a[0][0])**2 + (b[1][0] - a[1][0])**2

class Centroid():
    def __init__(self, xy):
        self.xy = xy

class TrackedCentroid(Centroid):
    def __init__(self, centroid):
        # does not work in maixpy micropython...
        # self.__dict__ = centroid.__dict__.copy()
        super().__init__(centroid.xy);
        self.path = [centroid.xy]

        self.KF = KalmanFilter(0.1, 1, 1, 1, 0.1,0.1)
        self.cab = 0

class CentroidTracker:
    def __init__(self):
        self.centroids = dict()
        # max amount of consecutive frames a centroid should exist while not
        # being detected
        self.maxcab   = 25
        # min squared distance between points in path (to save some memory)
        self.minpdist = 10**2
        # max squared distance between measured centroids and predicted centroids
        self.maxdist  = 50**2
        self.nextid   = 0
        # Determines whether path of each centroid should be stored
        self._pathc   = False

    @property
    def pathc(self):
        return self._pathc

    @pathc.setter
    def pathc(self, val):
        if val:
            self._pathc = True
        else:
            self._pathc = False
            for id in self.centroids.keys():
                self.clr_path(id)


    def register(self, centroid):
        id = self.nextid
        self.centroids[id] = TrackedCentroid(centroid)

        self.centroids[id].xy = self.centroids[id].KF.update(self.centroids[id].xy)
        self.centroids[id].cab = 0
        self.nextid += 1

    def deregister(self, id):
        del self.centroids[id]

    def clr_path(self, id):
        self.centroids[id].path = [self.centroids[id].xy]

    def inc_cab(self, id):
        self.centroids[id].cab += 1
        if self.centroids[id].cab > self.maxcab:
            self.deregister(id)

    def clr_cab(self, id):
        self.centroids[id].cab = 0

    def update(self, bboxs):
        if bboxs == None:
            for id in self.centroids.keys():
                predict = self.centroids[id].KF.predict()
                self.centroids[id].xy = self.centroids[id].KF.update(predict)
                self.inc_cab(id)
            return self.centroids

        measured_centroids = []
        predicted_centroids = self.centroids.copy()
        for id in predicted_centroids.keys():
            predicted_centroids[id] = Centroid(predicted_centroids[id].KF.predict())

        for bbox in bboxs:
            x = int(bbox.x() + bbox.w() // 2)
            y = int(bbox.y() + bbox.h() // 2)
            c = Centroid(ul.array([[x],[y]], dtype=ul.int16))
            measured_centroids.append(c)

            dist = -1
            cid = -1
            for id, pc in list(predicted_centroids.items()):
                cur_dist = sqeuclidean(c.xy, pc.xy)

                if cur_dist < self.maxdist:
                    if (cur_dist < dist) or (dist == -1):
                        dist = cur_dist
                        cid = id

            # Match found
            if cid != -1:
                self.centroids[cid].xy = self.centroids[cid].KF.update(c.xy)

                if self.pathc:
                    path_dist = sqeuclidean(self.centroids[cid].xy,
                                            self.centroids[cid].path[-1])
                    if path_dist >= self.minpdist:
                        self.centroids[cid].path.append(self.centroids[cid].xy)

                # remove updated centroids and clear cab
                del predicted_centroids[cid]
                self.clr_cab(cid)
                # Remove measurement from list, we matched it against a prediction
                del measured_centroids[-1]

        # Remaining centroids in the predicted list correspond to centroids who
        # potentially disappeard
        for id in predicted_centroids.keys():
            predict = self.centroids[id].KF.predict()
            self.centroids[id].xy = self.centroids[id].KF.update(predict)
            self.inc_cab(id)

        # Remaining centroid in measured list had no match so they need to be
        # registered
        for c in measured_centroids:
            self.register(c)

        return self.centroids
