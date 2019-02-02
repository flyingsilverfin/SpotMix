import requests
import time

class SpotifyAuth():
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret


    def token(self):
        if time.time > self._web_access_token_expiry:
            self._web_api_auth()
        return self._web_access_token

    def _web_api_auth(self):

        headers = {"Authorization": "Basic {0}:{1}".format(self._app_id, self._app_secret)}
        data = {"grant_type": "client_credentials"}
        response = requests.get("https://accounts.spotify.com/api/token", headers=headers, data=data).json()

        self._web_access_token = response['access_token']
        self._web_access_token_expiry = response['expires_in'] + time.time() - 2


