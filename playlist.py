from track import Track

class Playlist():

    def __init__(self, *track_ids):

        self._tracks = []

        for track_id in track_ids:
            track = Track(track_id)
            self._tracks.append(track)

    def add_track(self, track):
        if not type(track) == Track:
            raise Exception("Cannot add objects that are not Tracks to playlists")
        self._tracks.append(track)

    def size(self):
        return len(self._tracks)

    def tracks(self):
        return self._tracks

    def analyse(self, analyser):
        for track in self._tracks:
            track.vectorize(analyser)

    def __str__(self):
        s = "Playlist:"
        for track in self._tracks:
            s += "\n  {0}".format(track.__str__())
        return s
        





