"""Helpers for loading JSON into models, cleaning API responses and reading package metadata."""

import importlib.util
import json
from importlib.metadata import metadata
from pathlib import Path

from pydantic import BaseModel


def replace_empty_objects_with_null(data: object) -> object:
    """
    Recursively replace any dictionaries or lists that contain only None values with None.

    Any data that is not a dictionary or list will be returned as is.

    Parameters
    ----------
    data : object
        The data to check for empty dictionaries or lists

    Returns
    -------
    object
        The data with empty dictionaries or lists replaced with None
    """
    if isinstance(data, dict):
        if all(value is None for value in data.values()):
            return None
        return {key: replace_empty_objects_with_null(value) for key, value in data.items()}
    if isinstance(data, list):
        return [replace_empty_objects_with_null(item) for item in data]
    return data


def load_file_and_validate_to_model[T: BaseModel](file_path: str, type_to_parse: type[T]) -> T:
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
    json_data = json.loads(Path(file_path).read_text())
    return load_dict_to_model(json_data, type_to_parse)


def load_dict_to_model[T: BaseModel](json_data: dict, type_to_parse: type[T]) -> T:
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

    Raises
    ------
    ValidationError
        If the data does not match the model
    """
    modified_data = replace_empty_objects_with_null(json_data)
    return type_to_parse.model_validate(modified_data)


def get_field_from_pyproject(field_name: str) -> str:
    """
    Get a specific field from package metadata.

    Parameters
    ----------
    field_name : str
        The name of the field to retrieve (e.g., "version", "description")

    Returns
    -------
    str
        The value of the specified field from package metadata
    """
    pyproject_to_importlib_field_mappings = {
        "version": "Version",
        "description": "Summary",
    }

    if importlib.util.find_spec("importlib.metadata") is not None:
        try:
            pkg_metadata = metadata("pycricinfo")
            mapped_field = pyproject_to_importlib_field_mappings.get(field_name, field_name.capitalize())
            value = pkg_metadata.get(mapped_field, "")
            if value:
                return value
        except (ImportError, KeyError):
            pass

    return ""
