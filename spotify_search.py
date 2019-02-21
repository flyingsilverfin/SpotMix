import requests


def search(query, token, offset=0, limit=10, entity_type="track"):
    headers = {
            "Authorization": "Bearer {0}".format(token),
            "Accept": "application/json",
            "Content-Type": "application/json"
            }
    response = requests.get("https://api.spotify.com/v1/search?q={0}&type={1}&limit={2}&offset={3}".format(query, entity_type, limit, offset), headers=headers)

    if response.status_code != 200:
        raise Exception(response.json())

    return response.json()


def get_track(track_id, token):
    headers = {
            "Authorization": "Bearer {0}".format(token),
            "Accept": "application/json",
            "Content-Type": "application/json"
            }

    response = requests.get("https://api.spotify.com/v1/tracks/{0}".format(track_id), headers=headers)

    if response.status_code != 200:
        raise Exception(response.json())

    return response.json()


