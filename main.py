import numpy as np
import itertools

from comparator import VectorComparator
from analyser import TrackAnalyser
from merge import RandomShuffleMerge
from auth import SpotifyAuth



def playlist_to_vectors(track_ids):
    vectors = []
    for track_id in track_ids:
        vectors.append(track_analyser.vector(track_id))
    return vectors




def calculate_sample_sizes(size_a, size_b, target_size):
    """ Return how many from A and B to sample to achieve the given target size """

    # TODO be more clever here

    # some default method that samples ratio-wise
    total = size_a + size_b
    ratio_a, ratio_b = float(size_a)/total, float(size_b)/total
    return int(target_size * ratio_a), int(target_size * ratio_b)



def combine_playlists(p1_tracks, p2_tracks, target_size=10):
    size_p1, size_p2 = len(p1_tracks), len(p2_tracks)
    p1_vectors = playlist_to_vectors(p1_tracks)
    p2_vectors = playlist_to_vectors(p2_tracks)

    p1_sample_num, p2_sample_num = calculate_sample_sizes(size_p1, size_p2, target_size)

    p1_indices, p2_indices = RandomShuffleMerge.merge(p1_vectors, p2_vectors, p1_sample_num, p2_sample_num)

    p1_track_ids = set([p1_tracks[index] for index in p1_indices])
    p2_track_ids = set([p2_tracks[index] for index in p2_indices])
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


APP_ID = "4660068b56c440b08777e8ee43dc4422"
APP_SECRET = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(APP_ID, APP_SECRET)

track_analyser = TrackAnalyser(auth)
combined = combine_playlists(playlist_1, playlist_2, target_size=5)
print(combined)
