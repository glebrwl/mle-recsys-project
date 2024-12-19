import requests
import logging

# Configure logging
logging.basicConfig(
    filename='test_service.log',
    filemode='w',
    level=logging.INFO
)

recommendations_url = "http://localhost:8000"
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

params = {"user_id": 1353637, "k": 10}
logging.info("Sending request to events service to get events for user_id=1353637")

resp = requests.post(events_store_url + "/get", headers=headers, params=params)

if resp.status_code != 200:
    logging.error(f"Failed to retrieve events. Status code: {resp.status_code}, Response: {resp.text}")
else:
    logging.info("Successfully retrieved events from events service")

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
        items.extend(item_similar_items.get("item_id_2", []))
        scores.extend(item_similar_items.get("score", []))

logging.info("Completed test script execution.")
