import asyncio
import logging
import uvloop
import aiohttp_cors
import spotipy

from aiohttp import web
from spotipy_oauth2 import (
    SpotifyOAuth,
    SpotifyClientCredentials,
)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)

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
        redirect_uri='http://localhost:8080/callback'
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
        redirect_uri='http://localhost:8080/callback'
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
    web.run_app(app)
