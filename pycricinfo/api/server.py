import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pycricinfo.api.endpoints.raw import router as raw_router
from pycricinfo.api.endpoints.seasons import router as seasons_router
from pycricinfo.api.endpoints.wrapper import router as wrapper_router
from pycricinfo.exceptions import CricinfoAPIException
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
app.include_router(seasons_router)


@app.exception_handler(CricinfoAPIException)
async def my_custom_exception_handler(request: Request, exc: CricinfoAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.output(),
    )


if __name__ == "__main__":
    uvicorn.run("pycricinfo.api.server:app", host="0.0.0.0", port=8000, reload=True)
