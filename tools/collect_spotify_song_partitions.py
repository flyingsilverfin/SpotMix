import requests
import time
import json
from auth import SpotifyAuth
from spotify_search import search

secret = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(client_secret=secret)



def extract_track_count(search_response):
    return search_response["tracks"]["total"]


def get_total_tracks_for_search_term(term):
    response = search(query=term, token=auth.token(), limit=1)
    num_tracks = extract_track_count(response)
    return num_tracks



# build up data structure

alphas = "abcdefghijklmnopqrstuvwxyz"
nums = "0123456789"


country_codes = open("tools/country_codes.txt").readlines()
registrant_symbols = alphas + nums 
year_symbols = nums
code_symbols = nums

prefix_length_next_char_choices = {
        2: registrant_symbols, 3: registrant_symbols, 4: registrant_symbols,
        5: year_symbols, 6: year_symbols, 
        7:code_symbols, 8:code_symbols, 9: code_symbols, 10: code_symbols, 11: code_symbols
}

def search_term(isrc_prefix):
    return "isrc:{0}*".format(isrc_prefix)

under_10k_term_counts = {}

new_prefixes = [c.strip() for c in country_codes]

iteration = 0
while len(new_prefixes) > 0:
    counts = {}
    for i, prefix in enumerate(new_prefixes):
        prefix = prefix.upper()

        # in case we hit the request limit, put in a loop
        failed = True
        while failed:
            try:
                counts[prefix] = get_total_tracks_for_search_term(search_term(prefix))
                print("{0}/{1}. {2} - {3}".format(i, len(new_prefixes), prefix+"*", counts[prefix]))
                failed = False
            except Exception:
                time.sleep(1)
                continue

    for prefix in list(counts.keys()):
        if counts[prefix] < 10000:
            under_10k_term_counts[prefix] = counts[prefix] 
            del counts[prefix]

    print("Number of terms under 10k: {0}, sum: {1}".format(len(under_10k_term_counts), sum(under_10k_term_counts.values())))

    print("Number of terms over 10k: {0}, sum: {1}".format(len(counts), sum(counts.values())))

    iteration += 1

    json.dump(under_10k_term_counts, open("tools/data/isrc_prefixed/under_10k_iter_{0}.json".format(iteration), 'w'))
    json.dump(counts, open("tools/data/isrc_prefixed/over_10k_iter_{0}.json".format(iteration), 'w'))


    # expand all the remaining terms by one character
    new_prefixes= []
    for term in list(counts.keys()):
        next_choices = prefix_length_next_char_choices[len(term)]
        new_prefixes += [term + s for s in next_choices]









