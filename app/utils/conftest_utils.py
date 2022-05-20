from google.cloud.firestore import Client


def delete_all_collection(fs: Client):
    docs = fs.collection('diary').stream()
    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
