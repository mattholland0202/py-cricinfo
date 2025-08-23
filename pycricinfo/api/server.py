import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from pycricinfo.api.endpoints.match import router as match_router
from pycricinfo.api.endpoints.play_by_play import router as play_by_play_router
from pycricinfo.api.endpoints.player import router as player_router
from pycricinfo.api.endpoints.raw import router as raw_router
from pycricinfo.api.endpoints.scorecard import router as scorecard_router
from pycricinfo.api.endpoints.seasons import router as seasons_router
from pycricinfo.api.endpoints.team import router as team_router
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
add_pagination(app)

app.include_router(raw_router)
app.include_router(match_router)
app.include_router(play_by_play_router)
app.include_router(player_router)
app.include_router(seasons_router)
app.include_router(scorecard_router)
app.include_router(team_router)


@app.exception_handler(CricinfoAPIException)
async def my_custom_exception_handler(request: Request, exc: CricinfoAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.output(),
    )


if __name__ == "__main__":
    uvicorn.run("pycricinfo.api.server:app", host="0.0.0.0", port=8000, reload=True)
