import os
import requests
import logging 
from dotenv import load_dotenv 
load_dotenv()

features_store_url = os.environ.get('FEATURES_STORE_URL')

logging.basicConfig(
    filename='test_feature_service.log',
    filemode='w',
    level=logging.INFO
)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"item_id": 17245, "k": 3}

logging.info("Sending request to features service.")
resp = requests.post(features_store_url +"/similar_items", headers=headers, params=params)
if resp.status_code == 200:
    logging.info("Status code: 200")
    similar_items = resp.json()
else:
    similar_items = None
    logging.info("Status code: {resp.status_code}")
    
print(similar_items)
logging.info("Similar items: {similar_items}")