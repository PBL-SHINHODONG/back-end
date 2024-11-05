import os
import joblib
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import places, users, visitedplaces

from huggingface_hub import hf_hub_download


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = hf_hub_download(
        repo_id="GomDue/kmodes_model", 
        filename="kmodes_model.joblib",
        token=os.getenv("HUGGING_FACE_TOKEN")
    )
    app.state.model = joblib.load(model_path)

    file_path = hf_hub_download(
        repo_id="GomDue/kmodes_model",
        filename="tafp_dataset.csv",
        token=os.getenv("HUGGING_FACE_TOKEN")
    )
    app.state.tafp_df = pd.read_csv(file_path)

    yield


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)
app.include_router(users.router)
app.include_router(visitedplaces.router)

@app.get("/")
async def healthcheck():
    return {"Health Check": "OK"}
