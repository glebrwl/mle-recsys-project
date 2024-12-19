import os 
import io
import boto3
import logging 
import requests 
from dotenv import load_dotenv

from fastapi import FastAPI 
from contextlib import asynccontextmanager

import pandas as pd

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

features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020" 
path_to_personal= "recsys/recommendations/personal_als.parquet"


logger = logging.getLogger('uvicorn.error')

class Recommendations:
    def __init__(self):
        self._recs = {'personal': None, 'default': None}
        self._stats = {
            'request_personal_count': 0,
            'request_default_count': 0,
        }
    
    def load(self, type, path, **kwargs):
        logger.info("Retrieving S3 credentials")
        s3 = get_session_student()
        bucket_name = os.environ.get('S3_BUCKET_NAME')

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = load_par_from_s3(bucket_name=bucket_name,
                                            path=path,
                                            s3_client=s3)
        if type == 'personal':
            self._recs[type] = self._recs[type].set_index('user_id')
        logger.info(f'Loaded')
    
    def get(self, user_id:int, k:int=20):
        if k > 20:
            logger.error(f"Number of recommendations cannot be more than 20. Requested: {k}")

        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error('No recommendatiions found')
            recs = []
        
        return recs
    
    def stats(self):
        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value}")

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids


@asynccontextmanager 
async def lifespan(app: FastAPI):
    logger.info('Starting')
    yield 
    logger.info('Stopping')

app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations")
async def recommendations(user_id:int, k:int = 20):
    rec_store = Recommendations()
    rec_store.load(
        type='personal',
        path=path_to_personal
    )
    recs = rec_store.get(user_id, k)

    return {"recs": recs} 
