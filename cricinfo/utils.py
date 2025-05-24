import json
import tomllib
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def replace_empty_objects_with_null(data: Any) -> Any:
    """
    Recursively replace any dictionaries or lists that contain only None values with None.
    Any data that is not a dictionary or list will be returned as is.

    Parameters
    ----------
    data : Any
        The data to check for empty dictionaries or lists

    Returns
    -------
    Any
        The data with empty dictionaries or lists replaced with None
    """
    if isinstance(data, dict):
        if all(value is None for value in data.values()):
            return None
        return {key: replace_empty_objects_with_null(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_empty_objects_with_null(item) for item in data]
    else:
        return data


def load_file_and_validate_to_model(file_path: str, type_to_parse: Type[T]) -> T:
    """
    Load a JSON file from disk and validate its contents against a Pydantic model.

    Parameters
    ----------
    file_path : str
        The path to the JSON file to load
    type_to_parse : Type[T]
        The Pydantic model to validate against

    Returns
    -------
    T
        An instance of the Pydantic model with the loaded data
    """
    with open(file_path, "r") as content:
        json_data = json.load(content)
        return load_dict_to_model(json_data, type_to_parse)


def load_dict_to_model(json_data: dict, type_to_parse: Type[T]) -> T:
    """
    Validate a dictionary against a Pydantic model.

    Parameters
    ----------
    json_data : dict
        The dictionary to validate
    type_to_parse : Type[T]
        The Pydantic model to validate against

    Returns
    -------
    T
        An instance of the Pydantic model with the loaded data
    """
    modified_data = replace_empty_objects_with_null(json_data)
    try:
        model = type_to_parse.model_validate(modified_data)
    except ValidationError as ex:
        print(ex)
        exit(1)

    return model


def get_field_from_pyproject(field_name: str) -> str:
    """
    Get a specific field from the `project` section of the `pyproject.toml` file.

    Parameters
    ----------
    field_name : str
        The name of the field to retrieve from the `project` section

    Returns
    -------
    str
        The value of the specified field from the `project` section of `pyproject.toml`
    """
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    project_section: dict = pyproject.get("project", {})

    return project_section.get(field_name)
