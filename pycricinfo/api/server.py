import uvicorn
from fastapi import FastAPI

from pycricinfo.api.endpoints.raw import router as raw_router
from pycricinfo.api.endpoints.wrapper import router as wrapper_router
from pycricinfo.utils import get_field_from_pyproject

app = FastAPI(
    version=get_field_from_pyproject("version"),
    title="pycricinfo API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "tryItOutEnabled": True,
    },
    description=get_field_from_pyproject("description"),
)

app.include_router(wrapper_router)
app.include_router(raw_router)


def start_api():
    """Start the FastAPI server with uvicorn."""
    uvicorn.run("pycricinfo.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start_api()
