"""HTTP layer for Cricinfo's JSON APIs and HTML pages: requests, sessions and bot-protection handling."""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from http import HTTPStatus
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import aiohttp
import yarl
from pydantic import BaseModel, ValidationError

try:
    from curl_cffi import requests as curl_requests
except ImportError:  # pragma: no cover - optional at runtime in some environments
    curl_requests = None

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.exceptions import CricinfoAPIException
from pycricinfo.utils import replace_empty_objects_with_null

logger = logging.getLogger("cricinfo")


_REDIRECT_STATUSES = (301, 302, 303, 307, 308)
_MAX_REDIRECTS = 10

_COMMON_BROWSER_HEADERS = {
    "DNT": "1",
    "Sec-GPC": "1",
    "Cache-Control": "max-age=0",
    "Pragma": "no-cache",
}


async def get_and_parse[T: BaseModel](  # noqa: PLR0913 - each argument is an independent request option
    route: str,
    type_to_parse: type[T],
    params: Optional[dict] = None,
    *,
    null_out_empty_dicts: bool = False,
    base_route: BaseRoute = BaseRoute.core,
    session: Optional[aiohttp.ClientSession] = None,
) -> T:
    """
    Make a GET request to the API and parse the response to the supplied type.

    Parameters
    ----------
    route : str
        The route template to call
    type_to_parse : Type[T]
        The source model type to attempt to parse the response into
    params : dict, optional
        Any parameters to fill in into the route, in a dictionary of key-value pairs, by default None
    null_out_empty_dicts : bool, optional
        Whether to replace any dictionaries that contain only None values with None, by default False
    base_route: BaseRoute, optional
        The base route to use for the API call, by default BaseRoute.core
    session : aiohttp.ClientSession, optional
        An existing session to use for the request. If None, a new session is created and
        closed after the request. Pass a session created by ``create_session()`` to persist
        cookies across multiple requests, by default None

    Returns
    -------
    T
        The response data parsed into the supplied model
    """
    api_response = await get_request(route, params, base_route=base_route, session=session)

    if null_out_empty_dicts:
        api_response = replace_empty_objects_with_null(api_response)

    try:
        return type_to_parse.model_validate(api_response)
    except ValidationError:
        logger.exception("Failed to parse response from '%s' into %s", route, type_to_parse.__name__)
        raise


async def get_request(  # noqa: PLR0913 - each argument is an independent request option
    route: str,
    params: Optional[dict[str, str]] = None,
    base_route: BaseRoute = BaseRoute.core,
    *,
    response_output_sub_folder: Optional[str] = None,
    warm_session: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> dict | str:
    """
    Make a GET request to the Cricinfo API or page routes.

    Parameters
    ----------
    route : str
        The route template to call
    params : dict[str, str], optional
        Any parameters to fill in into the route, in a dictionary of key-value pairs, by default None
    base_route: BaseRoute, optional
        The base route to use for the API call, by default BaseRoute.core
    response_output_sub_folder : str, optional
        Sub-folder within the response output folder to write the response file, by default None
    warm_session : bool, optional
        Whether to warm the session with a homepage navigation request before issuing the main request.
        Most useful for page routes that may require initial cookie setup, by default False
    session : aiohttp.ClientSession, optional
        An existing session to use for the request. If None, a new session is created and
        closed after the request. Pass a session created by ``create_session()`` to persist
        cookies across multiple requests, by default None

    Returns
    -------
    dict | str
        The JSON content or HTML text of the response
    """
    request_id = str(uuid.uuid4())
    response_logging_extras = {
        "cricket_stats.request_id": request_id,
        "cricket_stats.request_route_template": route,
    }

    if params:
        route = _format_route(route, params)

    full_route = f"{_get_base_url(base_route)}{route}"
    is_page = base_route in (BaseRoute.page, BaseRoute.stats)

    referer = full_route if base_route == BaseRoute.page else urljoin(full_route, urlparse(full_route).path)

    headers = _get_request_headers(base_route=base_route, referer=referer)

    logger.debug("Querying: %s", full_route, extra={"cricket_stats.request_id": request_id})

    async with _session_scope(session) as request_session:
        if warm_session and base_route == BaseRoute.page:
            await _warm_page_session(request_session)

        response = await _get_following_redirects(request_session, yarl.URL(full_route, encoded=True), headers)
        async with response:
            if is_page:
                output, response_status = await _read_page_response(
                    response, full_route, referer, headers["Origin"], response_logging_extras
                )
            else:
                output, response_status = await _read_api_response(response)

    response_logging_extras["cricket_stats.response_code"] = response_status

    if is_page:
        logger.debug(json.dumps(f"Page fetched from: {full_route}"), extra=response_logging_extras)
        output_for_file = output
        response_output_file_extension = "html"
    else:
        logger.debug(json.dumps(output, indent=4), extra=response_logging_extras)
        output_for_file = json.dumps(output, indent=4)
        response_output_file_extension = "json"

    _output_response_to_file(output_for_file, route, response_output_sub_folder, response_output_file_extension)

    if response_status != HTTPStatus.OK:
        logger.error(
            "Status Code '%s' returned for '%s'",
            response_status,
            full_route,
            extra=response_logging_extras,
        )
        raise CricinfoAPIException(status_code=response_status, route=full_route, content=output)

    return output


def _get_base_url(base_route: BaseRoute) -> str:
    """
    Get the base URL for a base route type.

    Parameters
    ----------
    base_route : BaseRoute
        The base route type being requested

    Returns
    -------
    str
        The base URL that routes are appended to
    """
    if base_route == BaseRoute.core:
        return get_settings().core_base_route_v2
    if base_route == BaseRoute.site:
        return get_settings().site_base_route_v2
    if base_route == BaseRoute.stats:
        return get_settings().stats_base_route
    return get_settings().cricinfo_base_route


@asynccontextmanager
async def _session_scope(session: Optional[aiohttp.ClientSession]) -> AsyncGenerator[aiohttp.ClientSession]:
    """
    Yield the supplied session, or a new one that is closed on exit if none was supplied.

    Parameters
    ----------
    session : aiohttp.ClientSession, optional
        An existing session, which is left open on exit

    Returns
    -------
    AsyncGenerator[aiohttp.ClientSession]
        The session to make requests with
    """
    if session is not None:
        yield session
        return

    owned_session = create_session()
    try:
        yield owned_session
    finally:
        await owned_session.close()


async def _read_page_response(
    response: aiohttp.ClientResponse, full_route: str, referer: str, origin: str, logging_extras: dict[str, str]
) -> tuple[str, int]:
    """
    Read an HTML page response, retrying with browser TLS impersonation if blocked by bot protection.

    Parameters
    ----------
    response : aiohttp.ClientResponse
        The response to read
    full_route : str
        The URL that was requested, used for the retry
    referer : str
        The referer header value, used for the retry
    origin : str
        The origin header value, used for the retry
    logging_extras : dict[str, str]
        Logging extras for the request. The transport fallback and block reason are added to it when they apply

    Returns
    -------
    tuple[str, int]
        The HTML text of the page and the effective status code
    """
    response_status = response.status
    output = await response.text()

    if response_status == HTTPStatus.FORBIDDEN or _is_bot_protection_page(output):
        fallback_output = await _retry_with_browser_tls(full_route=full_route, referer=referer, origin=origin)
        if fallback_output is not None:
            output = fallback_output
            response_status = HTTPStatus.OK
            logging_extras["cricket_stats.transport_fallback"] = "curl_cffi"

    if _is_bot_protection_page(output):
        response_status = HTTPStatus.FORBIDDEN
        logging_extras["cricket_stats.block_reason"] = "bot_protection_page"

    return output, response_status


async def _read_api_response(response: aiohttp.ClientResponse) -> tuple[dict | str, int]:
    """
    Read a JSON API response.

    Parameters
    ----------
    response : aiohttp.ClientResponse
        The response to read

    Returns
    -------
    tuple[dict | str, int]
        The JSON content of the response (or its raw text, for a non-JSON error response) and the status code

    Raises
    ------
    ValueError
        If a 200 response does not have a JSON body
    """
    try:
        return await response.json(content_type=None), response.status
    except ValueError:
        # Error responses may not have a JSON body, so fall back to the raw text and let the status
        # code check in get_request raise a CricinfoAPIException
        if response.status == HTTPStatus.OK:
            raise
        return await response.text(), response.status


def _format_route(route: str, params: Optional[dict[str, str]] = None) -> str:
    """
    Format the route with the provided parameters.

    Parameters
    ----------
    route : str
        The route template to format
    params : dict[str, str]
        The parameters to fill in into the route

    Returns
    -------
    str
        The formatted route
    """
    if params is None:
        params = {}
    for key, value in params.items():
        placeholder = key if key.startswith("{") else "{" + key
        placeholder = placeholder if placeholder.endswith("}") else placeholder + "}"
        route = route.replace(placeholder, str(value))
    return route


def _get_request_headers(base_route: BaseRoute, referer: str) -> dict[str, str]:
    """
    Build request-specific headers for page and API routes.

    Parameters
    ----------
    base_route : BaseRoute
        Which base route type is being requested.
    referer : str
        The referer value to attach to the request.

    Returns
    -------
    dict[str, str]
        Headers to send for the outgoing request.
    """
    if base_route in (BaseRoute.page, BaseRoute.stats):
        origin = (
            get_settings().stats_base_route.rstrip("/")
            if base_route == BaseRoute.stats
            else get_settings().cricinfo_base_route.rstrip("/")
        )
        return {
            "Referer": referer,
            "Origin": origin,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            **_COMMON_BROWSER_HEADERS,
        }

    return {
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }


def _is_bot_protection_page(content: str) -> bool:
    """Detect Akamai bot protection responses, including challenge and deny pages."""
    lowered = content.lower()
    return any(
        marker in lowered
        for marker in (
            "<title>access denied</title>",
            "errors.edgesuite.net",
            'id="sec-if-cpt-container"',
            "powered and protected by",
            "scf-akamai-logo",
        )
    )


async def _retry_with_browser_tls(full_route: str, referer: str, origin: str) -> str | None:
    """
    Retry blocked page requests with browser TLS fingerprint impersonation.

    This addresses environments where server egress IP/TLS fingerprints are
    blocked by WAF rules for some endpoints.
    """
    if curl_requests is None:
        return None

    fallback_headers = {
        "Referer": referer,
        "Origin": origin,
        "User-Agent": get_settings().page_headers.user_agent,
        "Accept": get_settings().page_headers.accept,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        **_COMMON_BROWSER_HEADERS,
    }

    def _do_request() -> str | None:
        try:
            response = curl_requests.get(
                full_route,
                headers=fallback_headers,
                impersonate="firefox",
                timeout=20,
            )
        except curl_requests.RequestsError as ex:
            logger.warning("Fallback page request failed: %s", ex)
            return None

        if response.status_code != HTTPStatus.OK or _is_bot_protection_page(response.text):
            return None

        return response.text

    return await asyncio.to_thread(_do_request)


def create_session() -> aiohttp.ClientSession:
    """
    Create a configured aiohttp ClientSession with base headers set.

    Reusing a session across multiple requests persists cookies returned by the
    server, making subsequent requests appear more like a real browser session.
    The caller is responsible for closing the session when finished.

    Returns
    -------
    aiohttp.ClientSession
        A session configured with appropriate browser-like default headers.
    """
    headers = {
        "User-Agent": get_settings().page_headers.user_agent,
        "Accept": get_settings().page_headers.accept,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        **_COMMON_BROWSER_HEADERS,
        "Connection": "keep-alive",
    }
    return aiohttp.ClientSession(headers=headers)


async def _warm_page_session(session: aiohttp.ClientSession) -> None:
    """
    Prime a session with a homepage navigation request to establish cookies.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The session to warm before making page requests.
    """
    warmup_url = "https://www.espncricinfo.com/"
    warmup_headers = {
        "Referer": warmup_url,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    response = await _get_following_redirects(session, yarl.URL(warmup_url, encoded=True), warmup_headers)
    response.release()


async def _get_following_redirects(
    session: aiohttp.ClientSession, url: yarl.URL, headers: dict[str, str]
) -> aiohttp.ClientResponse:
    """
    Make a GET request, following redirects without re-normalising the ``Location`` header.

    aiohttp parses ``Location`` with ``yarl.URL(location)``, which decodes ``%2F`` in the query back to ``/``. Cricinfo
    redirects split-season URLs (``season=2026/27``) to their encoded form (``season=2026%2F27``), so aiohttp's own
    redirect handling requests the original URL again and loops until ``TooManyRedirects``.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The session to make the request with
    url : yarl.URL
        The URL to request
    headers : dict[str, str]
        Headers to send with each request

    Returns
    -------
    aiohttp.ClientResponse
        The final, non-redirect response. The caller is responsible for releasing it.

    Raises
    ------
    aiohttp.TooManyRedirects
        If more than ``_MAX_REDIRECTS`` redirects are followed
    """
    history = []
    for _ in range(_MAX_REDIRECTS + 1):
        response = await session.get(url, headers=headers, allow_redirects=False)
        location = response.headers.get("Location")
        if response.status not in _REDIRECT_STATUSES or not location:
            return response

        response.release()
        history.append(response)
        url = url.join(yarl.URL(location, encoded=True))
        logger.debug("Following %s redirect to: %s", response.status, url)

    raise aiohttp.TooManyRedirects(history[0].request_info, tuple(history))


def _output_response_to_file(response: str, route: str, sub_folder: str, file_extension: str) -> None:
    """
    Output the content of the response to a file.

    Parameters
    ----------
    response : str
        The API/page response
    route : str
        The route that was called
    """
    folder = Path(get_settings().api_response_output_folder)
    now = datetime.now(UTC)
    today = now.strftime("%Y%m%d")
    file_name = f"{now.strftime('%H%M%S')}_{route.replace('/', '_')}.{file_extension}"

    if sub_folder:
        folder = folder / sub_folder
    folder = folder / today
    folder.mkdir(parents=True, exist_ok=True)

    file_path = (folder / file_name).resolve()
    file_path.write_text(response)
