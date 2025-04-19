from fastapi import FastAPI

from cricinfo.config import get_settings
from cricinfo.api.endpoints.wrapper import router


app = FastAPI(
    version=get_settings().APP_VERSION,
    title="py-cricinfo API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "tryItOutEnabled": True,
    },
    description="An API to collect data from ESPN Cricinfo",
)

app.include_router(router)