from google.cloud.firestore import Client
from google.cloud.storage import Bucket
import requests_toolbelt

from app.main import app
from fastapi.testclient import TestClient

from config import DefaultSettings, RunningENV
from requests_toolbelt import sessions


def delete_all_collection(fs: Client):
    docs = fs.collection('diary').stream()
    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()


def delete_all_object(bucket: Bucket):
    blobs = list(bucket.list_blobs())
    bucket.delete_blobs(blobs)


def get_client(settings: DefaultSettings):
    if settings.env == RunningENV.TEST_PRODUCTION.value:
        return sessions.BaseUrlSession(base_url=settings.production_base_url)
    else:
        return TestClient(app)
