import os
import requests

from dotenv import load_dotenv 
load_dotenv()

import logging
logging.basicConfig(
    filename='test_service.log',
    filemode='w',
    level=logging.INFO
)

recommendations_url = os.environ.get('RECOMMENDATIONS_URL')
features_store_url = os.environ.get('FEATURES_STORE_URL')
events_store_url = os.environ.get('EVENTS_STORE_URL')
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


user_ids = [1453637, 1353637, 1337055]
for uid in user_ids:
    params = {"user_id": uid, "k": 10}
    print(f"{params}")
    logging.info(f"Sending request to events service to get events for user_id: {uid}")

    resp = requests.post(events_store_url + "/get", headers=headers, params=params)

    events = resp.json().get("events", [])
    logging.info(f"Events received: {events}")

    items = []
    scores = []
    if len(events) > 0:
        for item_id in events:
            logging.info(f"Requesting similar items for item_id={item_id}")
            similar_items_params = {"item_id": item_id, "k": 10}
            resp = requests.post(features_store_url + '/similar_items', headers=headers, params=similar_items_params)

            if resp.status_code != 200:
                logging.error(f"Failed to retrieve similar items for item_id={item_id}. Status code: {resp.status_code}, Response: {resp.text}")
                continue

            item_similar_items = resp.json()
            logging.info(f"Similar items for item_id={item_id}: {item_similar_items}")
            items.extend(item_similar_items.get("similar_items", []))
            scores.extend(item_similar_items.get("score", []))

logging.info("Completed test script execution.")
