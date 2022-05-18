from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from google.cloud.firestore import Client

from app.models import User
from app.schema.authentication import AccessToken
from app.schema.diary import CreateDiaryBody, DiaryDatabase, UpdateDiaryBody
from app.utils.firestore import document_to_diary


def create_diary(input: CreateDiaryBody, user: User, fs: Client):
    id = str(uuid4())

    # TODO Translate content and detect emotion
    time_created = datetime.now()
    time_updated = datetime.now()
    data = DiaryDatabase(
        id=id,
        content=input.content,
        translated_content=input.content,
        emotion="happy",
        user_id=str(user.id),
        time_created=time_created,
        time_updated=time_updated)
    fs.collection('diary').document(id).set(data.dict(exclude={"id"}))
    return data


def get_all_diary(fs: Client):
    documents = fs.collection('diary').get()
    diaries = [document_to_diary(docs) for docs in documents if document_to_diary(docs) is not None]
    return diaries


def get_diary_by_id(diary_id: str, fs: Client):
    document = fs.collection('diary').document(diary_id).get()
    if document.to_dict() is None:
        return None

    diary = document_to_diary(document)
    if diary is None:
        raise HTTPException(500, "This diary format is not correct")
    return diary


def get_diary_by_id_or_error(diary_id: str, fs: Client):
    document = fs.collection('diary').document(diary_id).get()
    if document.to_dict() is None:
        raise HTTPException(404, "There is no diary with id " + diary_id)

    diary = document_to_diary(document)
    if diary is None:
        raise HTTPException(500, "This diary format is not correct")
    return diary


def update_diary(diary: DiaryDatabase, body: UpdateDiaryBody, fs: Client):
    data = body.dict(exclude_none=True)

    for key, value in data.items():
        setattr(diary, key, value)
    diary.time_updated = datetime.now()

    print(diary.dict())
    fs.collection('diary').document(diary.id).update(diary.dict())
    return diary


def delete_diary(diary: DiaryDatabase, fs: Client):
    fs.collection('diary').document(diary.id).delete()
    return diary
