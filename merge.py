import numpy as np
import itertools
from comparator import VectorComparator
from playlist import Playlist

def score_playlist(playlist, comparator=VectorComparator.l2):
    """ Compute all pairwise scores and sum to get playlist score """
    # TODO could be refined to score two separate playlist halves rather than a combined one
    total_score = 0.0
    tracks = playlist.tracks()
    for (t1, t2) in itertools.combinations(tracks, 2):
        total_score += comparator(t1.vector(), t2.vector())
    return total_score

class RandomShuffleMerge():

    @staticmethod
    def _random_playlist(p1, p2, num_p1, num_p2):
        tracks_p1 = p1.tracks()
        tracks_p2 = p2.tracks()

        p1_indices, p2_indices = np.arange(0, p1.size()), np.arange(0, p2.size())
        p1_subsample = np.random.choice(p1_indices, num_p1, replace=False)
        p2_subsample = np.random.choice(p2_indices, num_p2, replace=True)

        merged = Playlist()
        for index in p1_subsample:
            merged.add_track(tracks_p1[index])
        for index in p2_subsample:
            merged.add_track(tracks_p2[index])

        return merged


    @staticmethod
    def merge(p1, p2, num_p1, num_p2, trials=100):
        """ up to `attempts` times, randomly select subsets of p1 and p2 and score, return indices of best shuffle """
    
        best_score = 0.0
        best_playlist = 0.0
        for _ in range(trials):
            merged = RandomShuffleMerge._random_playlist(p1, p2, num_p1, num_p2)
            score = score_playlist(merged)
            if score > best_score:
                best_score = score
                best_playlist = merged
    
        return best_playlist
   
class GreedyMerge():
    
    def __init__(self):
        pass
    
    """ 
    General idea:
    * calculate all pairwise similarities between track in playlist A to playlist B
    * Determine the order of picking, always starting with a0, b0 (in case we have an imbalanced number to pick from A and B)
    * Pick a starting a0. Choose b0 as the most similar track to a0.
    * Pick the next aK or bK as given by the order, choosing the best one by _total similarity to all prior chosen a0:K-1 or b0:K1_
    * If desired: repeat process from all starting a0's, choose the best total set
    """
    
"""
other formulations:
    * clustering based on original analysis vectors from spotify (how to enforce some from A and B are included?)
    * one massive optimisation determining best tradeoff between number of A and B tracks as well as similarity 
      (natural trade off here: K most similar tracks will likely stem from A or B entirely, forcing origin diversity vs similarity)
"""
