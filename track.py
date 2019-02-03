

class Track():

    def __init__(self, track_id):
        self._id = track_id
        self._vector = None

    def id(self):
        return self._id

    def vector(self):
        if self._vector is None:
            raise Exception("Track not analysed yet, no vector available")
        return self._vector

    def vectorize(self, track_analyser):
        self._vector = track_analyser.vector(self._id)

    def __str__(self):
        return self._id



