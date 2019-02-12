import requests
import numpy as np

class TrackAnalyser():

    # def __init__(self, auth, vector_keys=["danceability", "energy", "liveness", "acousticness", "valence", "instrumentalness", "speechiness", "mode", "tempo"], vector_normalization=[1, 1, 1, 1, 1, 1,1, 1, 100.0]):
    def __init__(self, auth, vector_keys=["danceability", "energy", "liveness", "acousticness", "valence", "instrumentalness", "speechiness"], vector_normalization=[1, 1, 1, 1, 1, 1,1]):
        self._auth = auth
        self._keys = vector_keys
        self._normalizers = vector_normalization

    def _retrieve_analysis(self, track_id):
        """
        # example data for a track

        {'danceability': 0.735,
        'energy': 0.578,
        'time_signature': 4,
        'track_href': 'https://api.spotify.com/v1/tracks/06AKEBrKUckW0KREUWRnvT',
        'type': 'audio_features',
        'loudness': -11.84,
        'mode': 0,
        'liveness': 0.159,
        'tempo': 98.002,
        'speechiness': 0.0461,
        'instrumentalness': 0.0902,
        'id': '06AKEBrKUckW0KREUWRnvT',
        'uri': 'spotify:track:06AKEBrKUckW0KREUWRnvT',
        'acousticness': 0.514,
        'duration_ms': 255349,
        'valence': 0.636,
        'analysis_url': 'https://api.spotify.com/v1/audio-analysis/06AKEBrKUckW0KREUWRnvT',
        'key': 5}
        """

        headers = {"Authorization": "Bearer {0}".format(self._auth.token())}
        response = requests.get("https://api.spotify.com/v1/audio-features/{0}".format(track_id), headers=headers)
        json = response.json()
        # check if the response is not empty
        if 'danceability' not in json:
            raise Exception("No track analysis found for track ID: {0}".format(track_id))

        return json

    def vector(self, track_id):
        json_analysis = self._retrieve_analysis(track_id)

        vector = []
        for i, key in enumerate(self._keys):
            vector.append(json_analysis[key]/self._normalizers[i])

        return np.array(vector)
