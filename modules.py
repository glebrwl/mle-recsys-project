import os 
# import pandas as pd
from utils import *

import logging 
logger = logging.getLogger('uvicorn.error')

k_max = os.environ.get('K_MAX_RECOMMENDATIONS')

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

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = load_par_from_s3(path=path,
                                            s3_client=s3)
        if type == 'personal':
            self._recs[type] = self._recs[type].set_index('user_id')
        logger.info(f'Loaded')
    
    def get(self, user_id:int, k:int=k_max):
        if k > k_max:
            logger.error(f"Number of recommendations cannot be more than {k_max}. Requested: {k}")

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

class SimilarItems:
    def __init__(self):
        self._similar_items = None
    
    def load(self, path, **kwargs):
        logger.info("Retrieving S3 credentials")
        s3 = get_session_student()
        
        logger.info(f"Loading data, type: {type}")
        self._similar_items = load_par_from_s3(path=path,
                                               s3_client=s3)
        self._similar_items = self._similar_items.rename(columns={'item_id_1':'main_item',
                                                                  'item_id_2':'similar_items'})
        logger.info(f"Loaded")
    
    def get(self, item_id:int, k:int=10):
        try:
            i2i = self._similar_items.loc[self._similar_items['main_item'] == item_id].head(k)
            i2i = i2i[['similar_items', 'score']].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"similar_items": [], "score": {}}
        
        return i2i

class EventsStore:

    def __init__(self, max_events_per_user = 10):
        self.events = {}
        self.max_events_per_user = max_events_per_user
    
    def put(self, user_id, item_id):
        user_events = self.events.get(user_id, [])
        self.events[user_id] = [item_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        if user_id in self.events.keys():
            user_events = self.events[user_id][:k]
        else:
            user_events = []
            logger.info(f"No events for user: {user_id}")
        
        return user_events