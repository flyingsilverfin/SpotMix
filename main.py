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



def combine_playlists(p1, p2, analyser, method, target_size=10):
    p1.analyse(analyser)
    p2.analyse(analyser)

    p1_sample_num, p2_sample_num = calculate_sample_sizes(p1.size(), p2.size(), target_size)

    # merged_playlist = RandomShuffleMerge.merge(p1, p2, p1_sample_num, p2_sample_num)
    merged_playlist = method.merge(p1, p2, p1_sample_num, p2_sample_num)

    return merged_playlist

    
playlist_easy_1 = Playlist(*[
    "6ztstiyZL6FXzh4aG46ZPD", # similar 10
    "3aw9iWUQ3VrPQltgwvN9Xu",
    "4yKZACkuudvfd600H2dQie",
    "7oPnZNl1acGA7ELxsNirrR",
    "0zbfxaHhnFQoKhQ189Z5Wa",
    "1BPybPVkDfUjFDvqG04l58",
    "0ec2YqaLnasKAES0iWMmhy",
    "0Pu71wxadDlB8fJXfjIjeJ",
    "1Ov4E4nE7E0yzeqpbhEE5g",
    "4hrae8atte6cRlSC9a7VCO",

    "4LihUZcWy0B6lGLqcJ8u9B", # different 10
    "7p4vHnYXkxlzvfePJVpcTr",
    "1aS5oaBNG6wsf186ZZMCzX",
    "4dGJf1SER1T6ooX46vwzRB",
    "7o2CTH4ctstm8TNelqjb51",
    "37ZJ0p5Jm13JPevGcx4SkF",
    "2P884dqfjksDMSzUZksfrS",
    "37Tmv4NnfQeb0ZgUC4fOJj",
    "6zZmwY5qasaw7QtobXKpZs",
    "1vxw6aYJls2oq3gW0DujAo"
])

playlist_easy_2 = Playlist(*[
    "6EZhFFNrOOZ6qIjgWCfW3K", # similar 10
    "3aImJnJlAgcE7bJ1NxthGt",
    "1KGi9sZVMeszgZOWivFpxs",
    "3NfxSdJnVdon1axzloJgba",
    "5kh9e4rLT6ObUl0GbyP1cl",
    "3jagJCUbdqhDSPuxP8cAqF",
    "7vTEzNVfiUIWX0QqsLadNA",
    "11mwFrKvLXCbcVGNxffGyP",
    "6aJ90LBl96bly9zuEH1U2X",
    "1G88BbuMts7HC0nHGoHmhv",

    "3ZrWmt3DGH75hItHp6uWLz", # different 10
    "3W2ZcrRsInZbjWylOi6KhZ",
    "1rfofaqEpACxVEHIZBJe6W",
    "2yZDLcMDNHB5kewZbknwjs",
    "2FRnxuLDZ4vSdvER2Xzrv2",
    "3wtIJv1PVcwGdNVeIfGNOd",
    "3zl7j5ua8mF4JDYuxrfo01",
    "5itOtNx0WxtJmi1TQ3RuRd",
    "0GjEhVFGZW8afUYGChu3Rr",
    "3evG0BIqEFMMP7lVJh1cSf"
])

human_match_suggestion = [
    "6EZhFFNrOOZ6qIjgWCfW3K", # similar 10
    "3aImJnJlAgcE7bJ1NxthGt",
    "1KGi9sZVMeszgZOWivFpxs",
    "3NfxSdJnVdon1axzloJgba",
    "5kh9e4rLT6ObUl0GbyP1cl",
    "3jagJCUbdqhDSPuxP8cAqF",
    "7vTEzNVfiUIWX0QqsLadNA",
    "11mwFrKvLXCbcVGNxffGyP",
    "6aJ90LBl96bly9zuEH1U2X",
    "1G88BbuMts7HC0nHGoHmhv",
    "6ztstiyZL6FXzh4aG46ZPD", # similar 10
    "3aw9iWUQ3VrPQltgwvN9Xu",
    "4yKZACkuudvfd600H2dQie",
    "7oPnZNl1acGA7ELxsNirrR",
    "0zbfxaHhnFQoKhQ189Z5Wa",
    "1BPybPVkDfUjFDvqG04l58",
    "0ec2YqaLnasKAES0iWMmhy",
    "0Pu71wxadDlB8fJXfjIjeJ",
    "1Ov4E4nE7E0yzeqpbhEE5g",
    "4hrae8atte6cRlSC9a7VCO"
]

APP_ID = "4660068b56c440b08777e8ee43dc4422"
APP_SECRET = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(APP_ID, APP_SECRET)

print("--------------- Greedy Merge ---------------------")
track_analyser = TrackAnalyser(auth)
greedy_merger = GreedyMerge(comparator=VectorComparator.l1)
combined = combine_playlists(playlist_easy_1, playlist_easy_2, track_analyser, method=greedy_merger, target_size=20)
print(combined)

print("--- Human playlist ---")
print("\n  ".join(human_match_suggestion))

accuracy = 0
for track in combined.tracks():
    if track.id() in human_match_suggestion:
        accuracy += 1
print("Human-computer match: {0}/{1}".format(accuracy, len(human_match_suggestion)))
