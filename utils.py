import os 
import io
import boto3
import pandas as pd

import logging
logger = logging.getLogger("uvicorn.error")

from dotenv import load_dotenv
load_dotenv()

def get_session_student():
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID_STUDENT'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY_STUDENT')
            )
        return client
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}", exc_info=True)
        return None

def load_par_from_s3(path, s3_client):
    try:
        parquet_buffer = io.BytesIO()
        s3_client.download_fileobj(os.environ.get('S3_BUCKET_NAME'), path, parquet_buffer)
        parquet_buffer.seek(0)
        df = pd.read_parquet(parquet_buffer)
        return df
    except Exception as e:
        logger.error(f"Error loading file from S3 (bucket={os.environ.get('S3_BUCKET_NAME')}, path={path}): {e}",
                     exc_info=True)
        return None

def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids