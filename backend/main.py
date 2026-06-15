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

from app.api.planner import router as planner_router
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