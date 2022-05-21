from google.cloud.firestore import Client
from google.cloud.storage import Bucket


def delete_all_collection(fs: Client):
    docs = fs.collection('diary').stream()
    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()


def delete_all_object(bucket: Bucket):
    blobs = list(bucket.list_blobs())
    bucket.delete_blobs(blobs)
