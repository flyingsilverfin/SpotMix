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


    def __init__(self, trials=100):
        self._trials = trials

    def _random_combined_playlist(self, p1, p2, num_p1, num_p2):
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

    def merge(self, p1, p2, num_p1, num_p2, trials=100):
        """ up to `attempts` times, randomly select subsets of p1 and p2 and score, return indices of best shuffle """
    
        best_score = 0.0
        best_playlist = 0.0
        for _ in range(trials):
            merged = self._random_combined_playlist(p1, p2, num_p1, num_p2)
            score = score_playlist(merged)
            print("Possible playlist has scored: {0}".format(score))
            if score > best_score:
                best_score = score
                best_playlist = merged
        print("Best playlist has scored: {0}".format(best_score))
    
        return best_playlist
   


class Graph():

    def __init__(self):
        self._adjacency = {}

        self._payloads = {}
        self._edge_weights = {}
        self._types_index = {}

    def add_node(self, node_id, node_type, node_payload):
        # save payload in map
        self._payloads[node_id] = node_payload

        # update types index
        if node_type not in self._types_index:
            self._types_index[node_type] = [node_id]
        else:
            self._types_index[node_type].append(node_id)

        # update adjacency
        if node_id not in self._adjacency:
            self._adjacency[node_id] = []

    def add_edge(self, start_id, end_id, weight):

        # update adjacencies
        adj_start = self._adjacency[start_id]
        if end_id not in adj_start:
            adj_start.append(end_id)

        adj_end = self._adjacency[end_id]
        if start_id not in adj_end:
            adj_end.append(start_id)

        # save weight
        self._edge_weights[(start_id, end_id)] = weight

    def edge_weight(self, start, end):
        if (start, end) in self._edge_weights:
            return self._edge_weights[(start, end)]
        else:
            return self._edge_weights[(end, start)]
    
    def nodes(self):
        return list(self._adjacency.keys())

    def get_nodes(self, node_type=None):
        return self._types_index[node_type]

    def neighbors(self, node_id):
        return self._adjacency[node_id]

    def contains(self, node_id):
        return node_id in self._adjacency

    def structural_copy(self):
        g = Graph()
        for node in self._adjacency.keys():
            for t in self._types_index:
                if node in self._types_index[t]:
                    node_type = t
                    break
            # pass payloads by reference
            node_payload = self._payloads[node]
            g.add_node(node, node_type, node_payload)

        for ((start, end), weight) in self._edge_weights.items():
            g.add_edge(start, end, weight)

        return g


    def payload(self, node):
        return self._payloads[node]

    def edge_weights(self):
        return list(self._edge_weights.values())

    def __str__(self):
        vertices = list(self._adjacency.keys())
        s = "Vertices:"
        for v in vertices:
            s += "\n  {0} - {1}".format(v, self._payloads[v])

        for edge, weight in self._edge_weights.items():
            s += "\n  ({0}, {1}) - {2}".format(edge[0], edge[1], weight) 

        return s



class GreedyMerge():
    
    def __init__(self):
        pass

    def merge(self, p1, p2, num_p1, num_p2):

        g = Graph()
        for track in p1.tracks():
            g.add_node(track.id(), "p1", track)

        for track in p2.tracks():
            g.add_node(track.id(), "p2", track)

        
        # add edge from all p1 to p2 tracks
        for p1_track in p1.tracks():
            for p2_track in p2.tracks():
                similarity = VectorComparator.l2(p1_track.vector(), p2_track.vector())
                g.add_edge(p1_track.id(), p2_track.id(), weight=similarity)

        # add all edges to each other too so we consider total playlist cohesiveness
        p1_tracks = p1.tracks()
        for (t1, t2) in itertools.combinations(p1_tracks, 2):
            similarity = VectorComparator.l2(t1.vector(), t2.vector())
            g.add_edge(t1.id(), t2.id(), weight=similarity)

        p2_tracks = p2.tracks()
        for (t1, t2) in itertools.combinations(p2_tracks, 2):
            similarity = VectorComparator.l2(t1.vector(), t2.vector())
            g.add_edge(t1.id(), t2.id(), weight=similarity)


        # graph now has pairwise similarities

        merge_map = {
            "p2" : num_p1,
            "p1" : num_p2
        }
        merge_orders = self._all_merge_orders(merge_map)

        best_graph, best_score = None, 0.0
        for merge_order in merge_orders:
            print("Merging order: {0}".format(merge_order))
            greedy_subgraph = self._greedy_merge(g, merge_order)
            score = self._score_graph(greedy_subgraph)
            if score > best_score:
                best_graph = greedy_subgraph
                best_score = score

        print("Best playlist score: {0}".format(best_score))

        return self._graph_to_playlist(best_graph)


    def _rotate(self, l, n):
        return l[-n:] + l[:-n]

    def _all_merge_orders(self, type_quantity_map):
        all_orders = []
        types = list(sorted(type_quantity_map.keys()))
        min_quantity = min(list(type_quantity_map.values()))
        required_length = sum(type_quantity_map.values())

        for rotation in range(len(type_quantity_map.keys())):
            type_order = self._rotate(types, rotation)
            # pick one of each first, but this order
            order = type_order[:] 
            copy = type_quantity_map.copy()
            while len(order) < required_length:
                for t in type_order:
                    total_required = type_quantity_map[t]
                    remaining_required = copy[t]
                    generate = int(total_required/min_quantity)
                    num_type = min(generate, remaining_required) 
                    order += [t] * num_type
                    copy[t] -= num_type
            all_orders.append(order)
        return all_orders

    def _greedy_merge(self, graph, merge_order):

        first_node_type = merge_order[0]
        first_node_options = graph.get_nodes(node_type=first_node_type)

        best_graph = None
        best_score = 0.0
        for node in first_node_options:

            # initialize graph
            subgraph = Graph()
            subgraph.add_node(node, first_node_type, graph.payload(node))

            for t in merge_order[1:]:
                node_options = graph.get_nodes(node_type=t)
                best_next_subgraph_score = 0.0
                best_next_subgraph = None
                for node in node_options:
                    if subgraph.contains(node):
                        # exclude nodes already in the subgraph
                        continue

                    # determine which next possible node produces the best score

                    sg = subgraph.structural_copy()
                    sg.add_node(node, t, graph.payload(node))
                    # add corresponding edges into sg
                    for end in graph.neighbors(node):
                        if sg.contains(end):
                            sg.add_edge(node, end, graph.edge_weight(node, end))

                    score = self._score_graph(sg)
                    if score > best_next_subgraph_score:
                        best_next_subgraph_score = score
                        best_next_subgraph = sg

                subgraph = best_next_subgraph

            # choose the best greedy subgraph chosen from each possible starting node
            score = self._score_graph(subgraph)
            print("Possible playlist has scored as graph/playlist: {0}".format(score))

            if score > best_score:
                best_score = score
                best_graph = subgraph

        return best_graph



    def _score_graph(self, graph):
        """ Compute total similarity score by summing all edge weights """
        return np.sum(graph.edge_weights())

    def _graph_to_playlist(self, graph):
        p = Playlist()
        for node in graph.nodes():
            track = graph.payload(node)
            p.add_track(track)
        return p





       
"""
other formulations:
    * clustering based on original analysis vectors from spotify (how to enforce some from A and B are included?)
    * one massive optimisation determining best tradeoff between number of A and B tracks as well as similarity 
      (natural trade off here: K most similar tracks will likely stem from A or B entirely, forcing origin diversity vs similarity)
"""
