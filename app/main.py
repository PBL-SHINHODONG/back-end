from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import places

app = FastAPI()

origins = [
    ["*"],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)

@app.get("/")
async def healthcheck():
    return {"Health Check": "OK"}
