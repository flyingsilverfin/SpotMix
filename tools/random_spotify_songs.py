import requests
import time
import json
from auth import SpotifyAuth

secret = open("client_secret.txt").readlines()[0].strip()

auth = SpotifyAuth(client_secret=secret)


def search(query, offset=0, limit=10, entity_type="track"):
    headers = {
            "Authorization": "Bearer {0}".format(auth.token()),
            "Accept": "application/json",
            "Content-Type": "application/json"
            }
    response = requests.get("https://api.spotify.com/v1/search?q=\"{0}\"&type={1}&limit={2}&offset={3}".format(query, entity_type, limit, offset), headers=headers)

    if response.status_code != 200:
        raise Exception(response.json())

    return response.json()



def extract_track_count(search_response):
    return search_response["tracks"]["total"]



def get_total_tracks_for_search_term(term):
    response = search(query=term, limit=1)
    num_tracks = extract_track_count(response)
    return num_tracks



# build up data structure

symbols = "abcdefghijklmnopqrstuvwxyz+"

under_10k_term_counts = {}

counts = {s:None for s in symbols}

iteration = 0
while len(counts) > 0:
    # expand all the remaining terms by one character
    new_terms = []
    for term in list(counts.keys()):
        new_terms += [term + s for s in symbols]

    # save the expanded terms counts 
    counts = {}
    for i, term in enumerate(new_terms):

        # in case we hit the request limit, put in a loop
        failed = True
        while failed:
            try:
                counts[term] = get_total_tracks_for_search_term(term)
                print("{0}/{1}. {2} - {3}".format(i, len(new_terms), term, counts[term]))
                failed = False
            except Exception:
                time.sleep(1)
                continue

    for term in list(counts.keys()):
        if counts[term] < 10000:
            under_10k_term_counts[term] = counts[term] 
            del counts[term]

    print("Number of terms under 10k: {0}, sum: {1}".format(len(under_10k_term_counts), sum(under_10k_term_counts.values())))

    print("Number of terms over 10k: {0}, sum: {1}".format(len(counts), sum(counts.values())))


    iteration += 1

    json.dump(under_10k_term_counts, open("tools/data/under_10k_iter_{0}.json".format(iteration), 'w'))
    json.dump(counts, open("tools/data/over_10k_iter_{0}.json".format(iteration), 'w'))








