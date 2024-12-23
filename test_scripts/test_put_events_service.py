import os
import requests
import logging 
from dotenv import load_dotenv 
load_dotenv()

events_store_url = os.environ.get('EVENTS_STORE_URL')

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1337055, "item_id": 17245}

logging.basicConfig(
    filename='test_put_events_service.log',
    filemode='w',
    level=logging.INFO
)

logging.info("Sending request to put events to events service.")
resp = requests.post(events_store_url + "/put", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
    logging.info(f"Status code: 200")
else:
    result = None
    print(f"Status code: {resp.status_code}")
    logging.error(f"Status code: {resp.status_code}")
    
print(result)
logging.info(result)