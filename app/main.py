import os
import joblib
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import places, users, visitedplaces, menus, reviews, search

from huggingface_hub import hf_hub_download
from tensorflow.keras.models import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

    model_path = hf_hub_download(
        repo_id="GomDue/kmodes_model", 
        filename="kmodes_model.joblib",
        token=HUGGING_FACE_TOKEN
    )
    app.state.c_model = joblib.load(model_path)

    model_path = hf_hub_download(
        repo_id="GomDue/collaborative_filtering_model", 
        filename="collaborative_filtering_model.h5",
        token=HUGGING_FACE_TOKEN
    )
    app.state.cf_model = load_model(model_path)

    file_path = hf_hub_download(
        repo_id="GomDue/kmodes_model",
        filename="tafp_dataset.csv",
        token=HUGGING_FACE_TOKEN
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
app.include_router(menus.router)
app.include_router(reviews.router)
app.include_router(search.router)

@app.get("/")
async def healthcheck():
    return {"Health Check": "OK"}
