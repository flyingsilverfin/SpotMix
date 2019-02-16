import asyncio
import logging
import uvloop
import aiohttp_cors
import spotipy
import ssl

import aiohttp
from aiohttp import web
from spotipy_oauth2 import (
    SpotifyOAuth,
    SpotifyClientCredentials,
)

port=8080

from analyser import TrackAnalyser
from auth import SpotifyAuth
from tools.random_spotify_song import get_random_track_with_analysis
from tools.training_data_db import TrackSimilarityDb

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if port == 443:
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    certbase = "/etc/letsencrypt/live/www.mixit.app"
    sslcontext.load_cert_chain(certbase + "/fullchain.pem", certbase + "/privkey.pem")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    return web.json_response({
        'serverText': 'hello m8!'
    })


@routes.get('/geturl')
async def geturl(request):
    sp = SpotifyOAuth(
        client_id='',
        client_secret='',
        redirect_uri='http://localhost:{}/callback'.format(port)
    )
    url_to_show = sp.get_authorize_url(
        state="blah_blah",
        show_dialog=True,
    )
    return web.json_response({
        "url": url_to_show,
    })


@routes.get('/callback')
async def ping(request):
    token_from_spotify = request.rel_url.query['code'].split("&")[0]

    sp = SpotifyOAuth(
        client_id='',
        client_secret='',
        redirect_uri='http://localhost:{}/callback'.format(port)
    )

    token_info = sp.get_access_token(token_from_spotify)

    if token_info:
        access_token = token_info['access_token']
    else:
        return web.json_response({
            'fail': 'failed'
        })

    sp_real = spotipy.Spotify(auth=access_token)
    data = sp_real.me()
    display_name = data.get("display_name", None)

    if display_name:
        playlists = sp_real.user_playlists(display_name)
    else:
        return web.json_response({
            'fail': 'failed to get username'
        })

    return web.json_response({
        'playlists': playlists
    })






# ---- josh's shit code section that needs help AHHH ----

secret = open("client_secret.txt").readlines()[0].strip()
auth = SpotifyAuth(secret)
analyser = TrackAnalyser(auth)
db = TrackSimilarityDb("tools/data/track_similarities.db")

@routes.get("/similarity")
async def get_rate_track_similarity(request):
    template = open("tools/rate_similarity.html").readlines()

    random_id_1, _ = get_random_track_with_analysis(analyser, auth)
    random_id_2, _ = get_random_track_with_analysis(analyser, auth)

    # find and replace id 1
    template = [line.replace("REPLACE_ME_1", random_id_1) for line in template]
    template = [line.replace("REPLACE_ME_2", random_id_2) for line in template]

    resp = web.Response(body="\n".join(template).encode('utf-8'), content_type='text/html')
    resp.headers['content-type'] = 'text/html'
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    resp.headers["Pragma"] = "no-cache" # HTTP 1.0.
    resp.headers["Expires"] = "0" # Proxies.
    return resp 


@routes.post("/submit_similarity")
async def receive_rating(request):
    data = await request.post()
    print(data)
    try:
        id1 = data['id1']
        id2 = data['id1']
        rating = data['similarity']
        print("Adding {0}, {1} - {2}".format(id1, id2, rating))
        db.add(id1, id2, int(rating))
    except Exception as e:
        print("Exception!, {0}".format(e))

    return aiohttp.web.HTTPFound('/similarity')




if __name__ == "__main__":
    logger.info("Starting SpotMix!")

    app = web.Application()
    app.add_routes(routes)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    cors.add(app.router.add_resource("/geturl"))
    if port == 443:
        web.run_app(app, ssl_context=sslcontext, port=port)
    else:
        web.run_app(app, port=port)
