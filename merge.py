import numpy as np
import itertools
from comparator import VectorComparator

def score_playlist(playlist_vectors, comparator=VectorComparator.l2):
    """ Compute all pairwise scores and sum to get playlist score """
    # TODO could be refined to score two separate playlist halves rather than a combined one
    total_score = 0.0
    for (v1, v2) in itertools.combinations(playlist_vectors, 2):
        total_score += comparator(v1, v2)
    return total_score

class RandomShuffleMerge():

    @staticmethod
    def _random_playlist_index_combinations(p1_size, p2_size, num_p1, num_p2):
        p1_indices, p2_indices = np.arange(0, p1_size), np.arange(0, p2_size)
        p1_index_choices = np.random.choice(p1_indices, num_p1, replace=False)
        p2_index_choices = np.random.choice(p2_indices, num_p2, replace=False)
        return p1_index_choices, p2_index_choices

    @staticmethod
    def merge(p1_vectors, p2_vectors, num_p1, num_p2, trials=100):
        """ up to `attempts` times, randomly select subsets of p1 and p2 and score, return indices of best shuffle """
    
        best_score = 0.0
        best_p1_indices, best_p2_indices = None, None
        for _ in range(trials):
            p1_indices, p2_indices = RandomShuffleMerge._random_playlist_index_combinations(len(p1_vectors), len(p2_vectors), num_p1, num_p2)
            p1_song_vectors = [p1_vectors[index] for index in p1_indices]
            p2_song_vectors = [p2_vectors[index] for index in p2_indices]
    
            score = score_playlist(p1_song_vectors + p2_song_vectors)
            if score > best_score:
                best_p1_indices = p1_indices
                best_p2_indices = p2_indices
                best_score = score
    
        return best_p1_indices, best_p2_indices
   
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
