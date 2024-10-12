from fastapi import FastAPI

from .routers import places

app = FastAPI()

app.include_router(places.router)

@app.get("/")
async def healthcheck():
    return {"Health Check": "OK"}
