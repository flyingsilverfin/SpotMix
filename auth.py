import requests
import time
import base64

class SpotifyAuth():
    def __init__(self,client_secret, client_id="4660068b56c440b08777e8ee43dc4422"):
        self._client_id = client_id
        self._client_secret = client_secret

        self._web_access_token = None
        self._web_access_token_expiry = 0

    def token(self):
        if time.time() > self._web_access_token_expiry:
            self._web_api_auth()
        return self._web_access_token

    def _web_api_auth(self):

        auth_str = "{0}:{1}".format(self._client_id, self._client_secret)
        b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
        headers = {"Authorization": "Basic {0}".format(b64_auth_str)}
        data = {"grant_type": "client_credentials"}
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(response.json())
        
        token_data = response.json()

        self._web_access_token = token_data['access_token']
        self._web_access_token_expiry = token_data['expires_in'] + time.time() - 2


