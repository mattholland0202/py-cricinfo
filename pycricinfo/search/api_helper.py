import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.utils import replace_empty_objects_with_null

logger = logging.getLogger("cricinfo")
T = TypeVar("T", bound=BaseModel)


def get_and_parse(
    route: str,
    type_to_parse: Type[T],
    params: dict = None,
    null_out_empty_dicts: bool = False,
    base_route: BaseRoute = BaseRoute.core,
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
    Returns
    -------
    T
        The response data parsed into the supplied model
    """
    api_response = get_request(route, params, base_route)

    if null_out_empty_dicts:
        api_response = replace_empty_objects_with_null(api_response)

    try:
        return type_to_parse.model_validate(api_response)
    except ValidationError as ex:
        logger.error(ex)
        raise


def get_request(route: str, params: dict[str, str] = None, base_route: BaseRoute = BaseRoute.core) -> dict:
    """
    Make a GET request to the Football Stats API

    Parameters
    ----------
    route : str
        The route template to call
    params : dict[str, str], optional
        Any parameters to fill in into the route, in a dictionary of key-value pairs, by default None
    base_route: BaseRoute, optional
        The base route to use for the API call, by default BaseRoute.core
    Returns
    -------
    dict
        The JSON content of the API response
    """
    request_id = str(uuid.uuid4())
    response_logging_extras = {
        "cricket_stats.request_id": request_id,
        "cricket_stats.request_route_template": route,
    }

    if params:
        for key, value in params.items():
            if not key.startswith("{"):
                key = "{" + key
            if not key.endswith("}"):
                key = key + "}"
            route = route.replace(key, str(value))

    if base_route == BaseRoute.core:
        base = get_settings().core_base_route_v2
    else:
        base = get_settings().site_base_route_v2
    full_route = f"{base}{route}"

    logger.debug(f"Querying: {full_route}", extra={"cricket_stats.request_id": request_id})
    response = requests.get(full_route)

    json_content: dict = response.json()
    response_logging_extras["cricket_stats.response_code"] = response.status_code
    logger.debug(json.dumps(json_content), extra=response_logging_extras)

    _output_response_to_file(json_content, route)

    if response.status_code != 200:
        raise Exception(f"Status Code '{response.status_code}' returned for '{full_route}'")

    return json_content


def _output_response_to_file(json_content: dict, route: str) -> None:
    """
    Output the JSON content of the API Sports response to a file

    Parameters
    ----------
    json_content : dict
        The JSON content of the API response
    route : str
        The API route that was called
    """
    folder = Path(get_settings().api_response_output_folder)
    today = datetime.today().strftime("%Y%m%d")
    file_name = f"{datetime.now(UTC).time().strftime('%H%M%S')}_{route.replace('/', '_')}.json"

    folder = folder / today
    folder.mkdir(parents=True, exist_ok=True)

    file_path = (folder / file_name).resolve()
    with open(file_path, "w") as file:
        file.write(json.dumps(json_content, indent=4))
