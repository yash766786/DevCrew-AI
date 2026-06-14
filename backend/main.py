from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.planner import router as planner_router

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

app.include_router(planner_router)


@app.get("/")
def root():
    return {
        "message": "Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }