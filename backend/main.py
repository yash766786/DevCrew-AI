from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
import app.websocket.manager as ws_manager

@app.on_event("startup")
async def startup_event():
    ws_manager.main_loop = asyncio.get_running_loop()

    print("MAIN LOOP SAVED")

from app.api.project import router as project_router
from app.api.ws import router as ws_router

app.include_router(project_router)
app.include_router(ws_router)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }