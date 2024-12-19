import os
import io
import boto3
import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI

from dotenv import load_dotenv

logger = logging.getLogger("uvicorn.error")

load_dotenv()

def get_session_student():
    session = boto3.session.Session()
    return session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID_STUDENT'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY_STUDENT')
    )

def load_par_from_s3(bucket_name, path, s3_client):
    parquet_buffer = io.BytesIO()
    s3_client.download_fileobj(bucket_name, path, parquet_buffer)
    parquet_buffer.seek(0)
    df = pd.read_parquet(parquet_buffer)
    return df

class SimilarItems:
    def __init__(self):
        self._similar_items = None
    
    def load(self, path, **kwargs):
        logger.info("Retrieving S3 credentials")
        s3 = get_session_student()
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        
        logger.info(f"Loading data, type: {type}")
        self._similar_items = load_par_from_s3(bucket_name=bucket_name,
                                               path=path,
                                               s3_client=s3)
        logger.info(f"Loaded")
    
    def get(self, item_id:int, k:int=10):
        try:
            i2i = self._similar_items.loc[self._similar_items['item_id_1'] == item_id].head(k)
            i2i = i2i[['item_id_2', 'score']].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id_2": [], "score": {}}
        
        return i2i

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