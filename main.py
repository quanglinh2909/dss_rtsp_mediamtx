# -*- coding: utf-8 -*-
import logging
import os
from contextlib import asynccontextmanager

from app.config.database import database_manager_sqlite
from app.services.camera_service import camera_service
from app.websocket.websocket import router as api_router_ws
from starlette.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)

import uvicorn
from fastapi import FastAPI

from app.app import api_router
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting the server")
    database_manager_sqlite.create_tables()
    camera_service.load_all_camera()
    yield

    print("Shutting down the server")



app = FastAPI(
    docs_url="/docs",
    root_path="/dss",
    openapi_url="/openapi.json",
    title="DSS Backend API",
    lifespan=lifespan,
)
@app.get("/", response_class=HTMLResponse)
def get_camera_management_ui():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "camera_management.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

app.include_router(api_router_ws, prefix="/ws")

app.include_router(api_router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT)
