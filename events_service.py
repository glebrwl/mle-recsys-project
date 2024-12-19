from fastapi import FastAPI 

class EventsStore:

    def __init__(self, max_events_per_user = 10):
        self.events = {}
        self.max_events_per_user = max_events_per_user
    
    def put(self, user_id, item_id):
        if user_id not in self.events.keys():
            self.events[user_id] = []

        user_events = self.events[user_id]
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        if user_id in self.events.keys():
            user_events = self.events[user_id][:k]
        else:
            user_events = []
            print(f'No events for user: {user_id}')
        
        return user_events

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