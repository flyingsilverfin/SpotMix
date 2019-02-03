import numpy as np
import itertools

from comparator import VectorComparator
from analyser import TrackAnalyser
from merge import RandomShuffleMerge, GreedyMerge
from auth import SpotifyAuth
from playlist import Playlist



def calculate_sample_sizes(size_a, size_b, target_size):
    """ Return how many from A and B to sample to achieve the given target size """

    # TODO be more clever here

    # some default method that samples ratio-wise
    total = size_a + size_b
    ratio_a, ratio_b = float(size_a)/total, float(size_b)/total
    return int(target_size * ratio_a), int(target_size * ratio_b)



def combine_playlists(p1, p2, analyser, target_size=10):
    p1.analyse(analyser)
    p2.analyse(analyser)

    p1_sample_num, p2_sample_num = calculate_sample_sizes(p1.size(), p2.size(), target_size)

    # merged_playlist = RandomShuffleMerge.merge(p1, p2, p1_sample_num, p2_sample_num)
    merged_playlist = GreedyMerge.merge(p1, p2, p1_sample_num, p2_sample_num)

    return merged_playlist

    


playlist_1 = Playlist(*[
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
])

playlist_2 = Playlist(*[
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
])


APP_ID = "4660068b56c440b08777e8ee43dc4422"
APP_SECRET = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(APP_ID, APP_SECRET)

track_analyser = TrackAnalyser(auth)
combined = combine_playlists(playlist_1, playlist_2, track_analyser, target_size=5)
print(combined)
