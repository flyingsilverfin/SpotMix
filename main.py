import numpy as np
import itertools
import requests

token = open("token.txt").readlines()[0].strip()

def get_track(id="06AKEBrKUckW0KREUWRnvT"):
    headers = {"Authorization": "Bearer {0}".format(token)}
    return requests.get("https://api.spotify.com/v1/audio-features/{0}".format(id), headers=headers)


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


def track_json_to_vector(track_json):
    keys = ["danceability", "energy", "liveness", "acousticness", "valence", "instrumentalness", "speechiness"]
    vector = []
    for key in keys:
        try:
            vector.append(track_json[key])
        except Exception as e:
            print(e)
    return vector


def vector_similarity(v1, v2, method="l2"):
    v1, v2 = np.array(v1), np.array(v2)
    if method == "l2":
        return np.sum((v1-v2)**2)
    elif method == "l1":
        return np.sum(np.abs(v1 - v2))
    else:
        raise Exception("unknown loss {0}".format(method))


def playlist_json_to_vectors(playlist_jsons):
    vectors = []
    for song_json in playlist_jsons:
        vectors.append(track_json_to_vector(song_json))
    return vectors


def score_playlist(playlist_vectors, method="l2"):
    """ Compute all pairwise scores and sum to get playlist score """
    # TODO could be refined to score two separate playlist halves rather than a combined one
    total_score = 0.0
    for (v1, v2) in itertools.combinations(playlist_vectors, 2):
        total_score += vector_similarity(v1, v2, method=method)
    return total_score

def calculate_sample_sizes(size_a, size_b, target_size):
    """ Return how many from A and B to sample to achieve the given target size """

    # TODO be more clever here

    # some default method that samples ratio-wise
    total = size_a + size_b
    ratio_a, ratio_b = float(size_a)/total, float(size_b)/total
    return int(target_size * ratio_a), int(target_size * ratio_b)


def _random_playlist_index_combinations(p1_size, p2_size, num_p1, num_p2):
    p1_indices, p2_indices = np.arange(0, p1_size), np.arange(0, p2_size)
    p1_index_choices = np.random.choice(p1_indices, num_p1, replace=False)
    p2_index_choices = np.random.choice(p2_indices, num_p2, replace=False)
    return p1_index_choices, p2_index_choices


def random_shuffle_strategy(p1_vectors, p2_vectors, num_p1, num_p2, attempts=100):
    """ up to `attempts` times, randomly select subsets of p1 and p2 and score, return indices of best shuffle """

    best_score = 0.0
    best_p1_indices, best_p2_indices = None, None
    for _ in range(attempts):
        p1_indices, p2_indices = _random_playlist_index_combinations(len(p1_vectors), len(p2_vectors), num_p1, num_p2)
        p1_song_vectors = [p1_vectors[index] for index in p1_indices]
        p2_song_vectors = [p2_vectors[index] for index in p2_indices]

        score = score_playlist(p1_song_vectors + p2_song_vectors)
        if score > best_score:
            best_p1_indices = p1_indices
            best_p2_indices = p2_indices
            best_score = score

    return best_p1_indices, best_p2_indices



def combine_playlists(p1_json, p2_json, target_size=50):

    size_p1, size_p2 = len(p1_json), len(p2_json)
    p1_vectors = playlist_json_to_vectors(p1_json)
    p2_vectors = playlist_json_to_vectors(p2_json)

    p1_sample_num, p2_sample_num = calculate_sample_sizes(size_p1, size_p2, target_size)

    p1_indices, p2_indices = random_shuffle_strategy(p1_vectors, p2_vectors, p1_sample_num, p2_sample_num)


    p1_track_ids = set([p1_json[index]["id"] for index in p1_indices])
    p2_track_ids = set([p2_json[index]["id"] for index in p2_indices])
    return p1_track_ids.union(p2_track_ids)

    


playlist_1 = [
    "4CKVB4pANABYlWTXtobGGF",
    "401XEI0EwcNqSrB1i79p30",
    "13GFvIqm2nPtIokVQ53fTs",
    "2EFWnx5OAtpRSzLLTW8T57",
    "0xU5hglREQipGgY488h3aF",
    "1YdjpAX40I7SDJNUokG4V9",
    "4NVbnWdCbyFDeTfiI6Jo1G",
    "2BwLRDdMNqBPcjnKX26fnF",
    "1VjGmPQtaCv4SjNezSonyE",
    "7KOOHzDAxzl87i8VYk1iO2"
]

playlist_2 = [
    "19TJlkoBX756Vol2WBvwz4",
    "042gkptFZIyx7GNIwqQ0AL",
    "6ikyipe0mqiqwZcnaWPD5Q",
    "0ZOtv4ZfLsh9iGajvscBHK",
    "3jcw66OG8ZfqSY1fyxqovl",
    "1Szfm2XAx3Kgl55dyl8sTU",
    "4CH66Rxcjcj3VBHwmIBj4T",
    "2izx59095cl3TCR9e9WvLK",
    "4pvL3ihXYN9Ik8bgIaZEhq",
    "1UVsSga4bQ4H2oAmR4cuYx"
]

p1_json = [get_track(id).json() for id in playlist_1]
p2_json = [get_track(id).json() for id in playlist_2]
combined = combine_playlists(p1_json, p2_json, target_size=5)


print(combined)
