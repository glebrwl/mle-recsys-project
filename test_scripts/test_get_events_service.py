import os
import requests
import logging
from dotenv import load_dotenv 
load_dotenv()

events_store_url = os.environ.get('EVENTS_STORE_URL')

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1337055}

logging.basicConfig(
    filename='test_get_events_service.log',
    filemode='w',
    level=logging.INFO
)

logging.info("Sending request to get events from events service.")
resp = requests.post(events_store_url + "/get", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
    logging.error(f"status code: {resp.status_code}")
    
print(result) 
logging.info(result)