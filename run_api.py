import uvicorn
from fastapi import FastAPI

from pycricinfo.api.endpoints.wrapper import router
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

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
