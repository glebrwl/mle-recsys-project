from fastapi import FastAPI 

from modules import EventsStore

import logging
logger = logging.getLogger("uvicorn.error")

events_store = EventsStore()

app = FastAPI(title='events')

@app.post('/put')
async def put(user_id:int, item_id:int):
    """
    Сохраняет событие для user_id, item_id
    """
    events_store.put(user_id, item_id)
    return {"result": "ok"}

@app.post('/get')
async def get(user_id:int, k:int=10):
    """
    Возвращает список последних k событий для пользователя user_id
    """
    events = events_store.get(user_id, k)
    return {'events': events}