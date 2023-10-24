class Zone:
    def __init__(self, xy, wh, edge=True):
        self.edge = edge
        self.xy = xy
        self.wh = wh

    def inmeis(self, centroid):
        if self.xy[0] < centroid.xy[0][0] < (self.xy[0] + self.wh[0]) and \
           self.xy[1] < centroid.xy[1][0] < (self.xy[1] + self.wh[1]):
            return True
        else:
            return False

    def get_rect(self): #gg ez
        return (self.xy[0], self.xy[1], self.wh[0], self.wh[1])

class SchmittTrigger:
    def __init__(self, zones):
        self.zones  = zones
        self.visited = {}

    def update(self, centroids):
        output = []

        # delete items in visited if corresponding centroid doesn't exist
        for id in self.visited.keys():
            if id not in centroids:
                del self.visited[id]

        for id, centroid in centroids.items():
            for index, zone in enumerate(self.zones):
                if zone.inmeis(centroid) and:
                    if zone.edge:
                        if id not in self.visited:
                            self.visited[id] = [index]
                        elif index not in self.visited[id]:
                            self.visited[id].append(index)
                            output.append([int(id), self.visited.pop(id)])
                    elif id in self.visited and index not in self.visited[id]:
                        self.visited[id].append(index)
                    break

        return output
