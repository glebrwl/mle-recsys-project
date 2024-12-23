# import os
# import io
# import boto3
import logging
from contextlib import asynccontextmanager

from utils import *
from modules import SimilarItems

import pandas as pd
from fastapi import FastAPI

from dotenv import load_dotenv

logger = logging.getLogger("uvicorn.error")

load_dotenv()

sim_items_store = SimilarItems()

@asynccontextmanager
async def lifespan(app: FastAPI):
    sim_items_store.load(
        path='recsys/recommendations/similar.parquet'
    )
    logger.info("Ready!")
    yield 

app = FastAPI(title='features', lifespan=lifespan)

@app.post("/similar_items")
async def recommendations(item_id:int, k:int=10):
    i2i = sim_items_store.get(item_id, k)
    return i2i