import requests

def create_playlist(name, token, description="", public=True):

    headers = {
            "Authorization": "Bearer {0}".format(token),
            "Accept": "application/json",
            "Content-Type": "application/json"
    }

    data = {
            "name": name,
            "description": description,
            "public": public
    }

    response = requests.post("https://api.spotify.com/v1/me/playlists", data=data, headers=headers)

    if response.status_code != 200:
        raise Exception(response.json())

    playlist_id = response.json()["id"]
    return playlist_id


def add_tracks_to_playlist(playlist_id, track_ids, token):

    web_api = "https://api.spotify.com/v1/playlists/{0}/tracks?"
    track_uris = ["spotify:track:{}".format(tid) for tid in track_ids]

    params = "uris:{0}".format(",".join(track_uris))
    encoded_params = params.replace(",", "%2C").replace(":", "%3A")

    url = web_api + encoded_params

    headers = {
            "Authorization": "Bearer {0}".format(token),
            "Accept": "application/json",
            "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)

    if response.status_code != 200:
        raise Exception(response.json())

    return True

