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

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.exceptions import CricinfoAPIException
from pycricinfo.utils import replace_empty_objects_with_null

logger = logging.getLogger("cricinfo")
T = TypeVar("T", bound=BaseModel)


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
        "Connection": "keep-alive",
    }
    return aiohttp.ClientSession(headers=headers)


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
        base = get_settings().pages_base_route
    full_route = f"{base}{route}"

    referer = full_route if base_route == BaseRoute.page else urljoin(full_route, urlparse(full_route).path)

    if base_route == BaseRoute.page:
        sec_fetch_headers = {
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }
    else:
        sec_fetch_headers = {
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    headers = {
        "Referer": referer,
        **sec_fetch_headers,
    }

    logger.debug(f"Querying: {full_route}", extra={"cricket_stats.request_id": request_id})

    owned_session = session is None
    if owned_session:
        session = create_session()
    try:
        async with session.get(yarl.URL(full_route, encoded=True), headers=headers) as response:
            response_logging_extras["cricket_stats.response_code"] = response.status

            if base_route == BaseRoute.page:
                output = await response.text()
                logger.debug(json.dumps(f"Page fetched from: {full_route}"), extra=response_logging_extras)
                output_for_file = output
                response_output_file_extension = "html"
            else:
                output = await response.json()
                logger.debug(json.dumps(output, indent=4), extra=response_logging_extras)
                output_for_file = json.dumps(output, indent=4)
                response_output_file_extension = "json"

            _output_response_to_file(output_for_file, route, response_output_sub_folder, response_output_file_extension)

            if response.status != 200:
                logger.error(
                    f"Status Code '{response.status}' returned for '{full_route}'",
                    extra=response_logging_extras,
                )
                raise CricinfoAPIException(status_code=response.status, route=full_route, content=output)

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
