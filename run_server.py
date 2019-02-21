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

import argparse


import threading
import time
from analyser import TrackAnalyser
from auth import SpotifyAuth
from spotify_search import get_track
from tools.random_spotify_song import get_random_track_with_analysis
from tools.training_data_db import TrackSimilarityDb

parser = argparse.ArgumentParser()
parser.add_argument('-p', "--port", type=int, help="webserver port (443 uses ssl)", default=8080)
args = parser.parse_args()
port = args.port

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
track_buffer_limit = 200
track_id_buffer = []
min_buffered_track_popularity = 3


def next_valid_track_id():
    while True:
        try:
            time.sleep(0.05)
            track_id, _ = get_random_track_with_analysis(analyser, auth)
            print(track_id)
            track_popularity = int(get_track(track_id, auth.token())["popularity"])
            if track_popularity >= min_buffered_track_popularity:
                print("{0} - popularity: {1}".format(track_id, track_popularity))
                return track_id
        except Exception:
            time.sleep(0.1)
            # probably hit the rate limit

def refill_track_id_buffer():
    print("refilling buffer")
    while len(track_id_buffer) < track_buffer_limit:
        track_id_buffer.append(next_valid_track_id())

def pop_track_id():
    if len(track_id_buffer) < 2:
        return next_valid_track_id()
    else:
        return track_id_buffer.pop(0)

def sleep_apply(t, func):
    time.sleep(t)
    func()
    
refill_thread = threading.Thread(target=refill_track_id_buffer) 
refill_thread.start()


@routes.get("/similarity")
async def get_rate_track_similarity(request):
    global refill_thread
    template = open("html/rate_similarity.html").readlines()

    random_id_1 = pop_track_id()
    random_id_2 = pop_track_id()

    # find and replace id 1
    template = [line.replace("REPLACE_ME_1", random_id_1) for line in template]
    template = [line.replace("REPLACE_ME_2", random_id_2) for line in template]

    resp = web.Response(body="\n".join(template).encode('utf-8'), content_type='text/html')
    resp.headers['content-type'] = 'text/html'
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    resp.headers["Pragma"] = "no-cache" # HTTP 1.0.
    resp.headers["Expires"] = "0" # Proxies.

    # trigger a separate thread to run the refill buffer after a short delay
    if len(track_id_buffer) < track_buffer_limit/2 and not refill_thread.is_alive():
        refill_thread = threading.Thread(target=sleep_apply, args=(0.1, refill_track_id_buffer))
        refill_thread.start()

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

    app.router.add_static('/res', "html/res")

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
