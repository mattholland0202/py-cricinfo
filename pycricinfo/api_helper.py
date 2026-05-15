import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Type, TypeVar
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
T = TypeVar("T", bound=BaseModel)


_COMMON_BROWSER_HEADERS = {
    "DNT": "1",
    "Sec-GPC": "1",
    "Cache-Control": "max-age=0",
    "Pragma": "no-cache",
}


async def get_and_parse(
    route: str,
    type_to_parse: Type[T],
    params: dict = None,
    null_out_empty_dicts: bool = False,
    base_route: BaseRoute = BaseRoute.core,
    session: Optional[aiohttp.ClientSession] = None,
) -> T:
    """
    Make a GET request to the API and parse the response to the supplied type

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
    api_response = await get_request(route, params, base_route, session=session)

    if null_out_empty_dicts:
        api_response = replace_empty_objects_with_null(api_response)

    try:
        return type_to_parse.model_validate(api_response)
    except ValidationError as ex:
        logger.error(ex)
        raise


async def get_request(
    route: str,
    params: Optional[dict[str, str]] = None,
    base_route: BaseRoute = BaseRoute.core,
    response_output_sub_folder: str = None,
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

    if base_route == BaseRoute.core:
        base = get_settings().core_base_route_v2
    elif base_route == BaseRoute.site:
        base = get_settings().site_base_route_v2
    else:
        base = get_settings().cricinfo_base_route
    full_route = f"{base}{route}"

    referer = full_route if base_route == BaseRoute.page else urljoin(full_route, urlparse(full_route).path)

    headers = _get_request_headers(base_route=base_route, referer=referer)

    logger.debug(f"Querying: {full_route}", extra={"cricket_stats.request_id": request_id})

    owned_session = session is None
    if owned_session:
        session = create_session()
    try:
        if warm_session and base_route == BaseRoute.page:
            await _warm_page_session(session)

        async with session.get(yarl.URL(full_route, encoded=True), headers=headers) as response:
            response_status = response.status
            response_logging_extras["cricket_stats.response_code"] = response_status

            if base_route == BaseRoute.page:
                output = await response.text()

                if response_status == 403 or _is_bot_protection_page(output):
                    fallback_output = await _retry_with_browser_tls(full_route=full_route, referer=referer)
                    if fallback_output is not None:
                        output = fallback_output
                        response_status = 200
                        response_logging_extras["cricket_stats.response_code"] = response_status
                        response_logging_extras["cricket_stats.transport_fallback"] = "curl_cffi"

                if _is_bot_protection_page(output):
                    response_status = 403
                    response_logging_extras["cricket_stats.response_code"] = response_status
                    response_logging_extras["cricket_stats.block_reason"] = "bot_protection_page"

                logger.debug(json.dumps(f"Page fetched from: {full_route}"), extra=response_logging_extras)
                output_for_file = output
                response_output_file_extension = "html"
            else:
                output = await response.json()
                logger.debug(json.dumps(output, indent=4), extra=response_logging_extras)
                output_for_file = json.dumps(output, indent=4)
                response_output_file_extension = "json"

            _output_response_to_file(output_for_file, route, response_output_sub_folder, response_output_file_extension)

            if response_status != 200:
                logger.error(
                    f"Status Code '{response_status}' returned for '{full_route}'",
                    extra=response_logging_extras,
                )
                raise CricinfoAPIException(status_code=response_status, route=full_route, content=output)

            return output
    finally:
        if owned_session:
            await session.close()


def _format_route(route: str, params: dict[str, str] = {}) -> str:
    """
    Format the route with the provided parameters

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
    for key, value in params.items():
        if not key.startswith("{"):
            key = "{" + key
        if not key.endswith("}"):
            key = key + "}"
        route = route.replace(key, str(value))
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
    if base_route == BaseRoute.page:
        return {
            "Referer": referer,
            "Origin": get_settings().cricinfo_base_route.rstrip("/"),
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


async def _retry_with_browser_tls(full_route: str, referer: str) -> str | None:
    """
    Retry blocked page requests with browser TLS fingerprint impersonation.

    This addresses environments where server egress IP/TLS fingerprints are
    blocked by WAF rules for some endpoints.
    """
    if curl_requests is None:
        return None

    fallback_headers = {
        "Referer": referer,
        "Origin": get_settings().cricinfo_base_route.rstrip("/"),
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
                impersonate="chrome124",
                timeout=20,
            )
            if response.status_code != 200:
                return None

            response_text = response.text
            if _is_bot_protection_page(response_text):
                return None

            return response_text
        except Exception as ex:
            logger.warning("Fallback page request failed: %s", ex)
            return None

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

    async with session.get(yarl.URL(warmup_url, encoded=True), headers=warmup_headers):
        return


def _output_response_to_file(response: str, route: str, sub_folder: str, file_extension: str) -> None:
    """
    Output the content of the response to a file

    Parameters
    ----------
    response : str
        The API/page response
    route : str
        The route that was called
    """
    folder = Path(get_settings().api_response_output_folder)
    today = datetime.today().strftime("%Y%m%d")
    file_name = f"{datetime.now(UTC).time().strftime('%H%M%S')}_{route.replace('/', '_')}.{file_extension}"

    if sub_folder:
        folder = folder / sub_folder
    folder = folder / today
    folder.mkdir(parents=True, exist_ok=True)

    file_path = (folder / file_name).resolve()
    with open(file_path, "w") as file:
        file.write(response)
