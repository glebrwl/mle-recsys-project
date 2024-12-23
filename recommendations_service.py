import os 
import io
import boto3
import logging 
import requests 
from dotenv import load_dotenv

from utils import *
from modules import Recommendations

from fastapi import FastAPI 
from contextlib import asynccontextmanager

import pandas as pd

load_dotenv()

features_store_url = os.environ.get('FEATURES_STORE_URL')
events_store_url = os.environ.get('EVENTS_STORE_URL')
path_to_personal= os.environ.get('PATH_TO_PERSONAL')

logger = logging.getLogger('uvicorn.error')

@asynccontextmanager 
async def lifespan(app: FastAPI):
    logger.info('Starting')
    yield 
    logger.info('Stopping')

app = FastAPI(title="recommendations", lifespan=lifespan)

@app.post("/recommendations_offline")
async def recommendations_offline(user_id:int, k:int = 20):
    """
    Возвращает список оффлайн-рекомендаций длиной k для пользователя user_id
    """
    rec_store = Recommendations()
    rec_store.load(
        type='personal',
        path=path_to_personal
    )
    recs = rec_store.get(user_id, k)

    return {"recs": recs} 

@app.post("/recommendations_online")
async def recommendations_online(user_id:int, k:int=10):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    
    # получаем последнее событие пользователя
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]
    
    items = []
    scores = []
    if len(events) > 0:
        for item_id in events:
            params = {"item_id": item_id, "k": k}
            resp = requests.post(features_store_url + '/similar_items', headers=headers, params=params)
            item_similar_items = resp.json()
            items += item_similar_items["item_id_2"]
            scores += item_similar_items["score"]
        
        combined = list(zip(items, scores))
        combined = sorted(combined, key=lambda x: x[1], reverse=True)
        combined = [item for item, _ in combined]
        recs = dedup_ids(combined)
    else:
        recs = []

    return {"recs": recs} 

@app.post('/recommendations')
async def recommendations(user_id:int, k:int=30):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))

    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])
    
    if len(recs_offline) < len(recs_online):
        recs_blended.extend(recs_online[min_length:])
    elif len(recs_offline) > len(recs_online):
        recs_blended.extend(recs_offline[min_length:])
    
    recs_blended = dedup_ids(recs_blended)
    recs_blended = recs_blended[:k]
    return {"recs": recs_blended}