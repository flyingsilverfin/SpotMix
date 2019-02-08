import numpy as np
import json
from auth import SpotifyAuth
from spotify_search import search
from analyser import TrackAnalyser

secret = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(client_secret=secret)
analyser = TrackAnalyser(auth)

search_hits = json.load(open("tools/data/isrc_prefixed/under_10k_isrc_prefix_counts.json"))
search_keys, search_counts = list(search_hits.keys()), list(search_hits.values())
search_weights = np.array(search_counts)/np.sum(search_counts)


# sample query according to weight (ie. count)
def choose_random_query(queries, probs, quantity=1):
    return np.random.choice(queries, quantity, p=probs)


def get_random_track():
    query = choose_random_query(search_keys, search_weights, quantity=1)[0]
    query_hits = search_hits[query]
    offset = np.random.randint(0, query_hits)
    response = search(query="isrc:{0}*".format(query), token=auth.token(), limit=1, offset=offset)
    track = response["tracks"]["items"][0]

    print("Track id, title, author: {0},  {1} - {2}".format(track["id"], track["name"], ",".join([a["name"] for a in track["artists"]])))
    return track["id"]



def get_random_track_with_analysis():
    while True:
        random_track_id = get_random_track()
        try:
            analysis = analyser.vector(random_track_id)
            print(analysis)
            return random_track_id, analysis
        except Exception as e:
            print(e)
            continue
        










