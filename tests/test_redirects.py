import asyncio

import aiohttp
import pytest
import yarl
from aiohttp import web
from aiohttp.test_utils import TestServer

from pycricinfo.api_helper import _get_following_redirects

ENCODED_SEASON_PATH = "/ci/engine/series/index.html?season=2026%2F27;view=season"


async def _season_handler(request: web.Request) -> web.Response:
    # Mirror Cricinfo: redirect the unencoded split-season URL to its percent-encoded form
    if request.raw_path == ENCODED_SEASON_PATH:
        return web.Response(text="season page")
    # Set the header directly: web.HTTPMovedPermanently(location=...) would decode %2F itself
    return web.Response(status=301, headers={"Location": ENCODED_SEASON_PATH})


async def _loop_handler(request: web.Request) -> web.Response:
    raise web.HTTPFound(location="/loop")


async def _fetch(path: str) -> tuple[int, str, str]:
    app = web.Application()
    app.router.add_get("/ci/engine/series/index.html", _season_handler)
    app.router.add_get("/loop", _loop_handler)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        url = yarl.URL(f"{server.make_url('')}{path}", encoded=True)
        response = await _get_following_redirects(session, url, headers={})
        async with response:
            return response.status, await response.text(), response.url.raw_path_qs


def test_redirect_keeps_encoded_location():
    status, text, final_path = asyncio.run(_fetch("/ci/engine/series/index.html?season=2026/27;view=season"))
    assert status == 200
    assert text == "season page"
    assert final_path == ENCODED_SEASON_PATH


def test_redirect_loop_raises_too_many_redirects():
    with pytest.raises(aiohttp.TooManyRedirects):
        asyncio.run(_fetch("/loop"))
