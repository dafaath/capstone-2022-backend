from datetime import datetime
from uuid import uuid4

import six
from fastapi import HTTPException
from google.cloud.firestore import Client
from google.cloud.translate_v2 import Client as TranslateClient

from app.models import User
from app.schema.authentication import AccessToken
from app.schema.diary import (CreateDiaryBody, DiaryDatabase,
                              TranslateResponse, UpdateDiaryBody)
from app.utils.firestore import document_to_diary


def translate_content(input: str, translate_client: TranslateClient, translate: bool, target_language: str = "en"):
    if isinstance(input, six.binary_type):
        input = input.decode("utf-8")

    if translate:
        response: str = translate_client.translate(input, target_language="en")
        translate_response = TranslateResponse(**response)
    else:
        translate_response = TranslateResponse(
            translated_text=input,
            detected_source_language="id",
            input=input)
    return translate_response


def create_diary(input: CreateDiaryBody, user_id: str, fs: Client, translate_client: TranslateClient, translate=True):
    # TODO detect emotion
    translate_response = translate_content(input.content, translate_client, translate=translate)

    id = str(uuid4())
    time_created = datetime.now()
    time_updated = datetime.now()
    data = DiaryDatabase(
        id=id,
        title=input.title,
        content=input.content,
        translated_content=translate_response.translated_text,
        emotion="happy",
        user_id=user_id,
        time_created=time_created,
        time_updated=time_updated)
    fs.collection('diary').document(id).set(data.dict(exclude={"id"}))
    return data


def get_all_diary(page: int, size: int, fs: Client):
    ref = fs.collection('diary').order_by("user_id").order_by(
        "time_created", "DESCENDING")
    if page and size:
        offset = (page - 1) * size
        ref = ref.limit(size).offset(offset)

    documents = ref.get()
    diaries = [document_to_diary(docs) for docs in documents if document_to_diary(docs) is not None]
    return diaries


def get_user_diary(page: int, size: int, user_id: str, fs: Client):
    ref = fs.collection('diary').where("user_id", "==", user_id).order_by("time_created", "DESCENDING")
    if page and size:
        offset = (page - 1) * size
        ref = ref.limit(size).offset(offset)
    documents = ref.get()
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


def update_diary(
        diary: DiaryDatabase,
        body: UpdateDiaryBody,
        fs: Client,
        translate_client: TranslateClient,
        translate=True):
    data = body.dict(exclude_none=True)

    for key, value in data.items():
        setattr(diary, key, value)

    translate_response = translate_content(diary.content, translate_client, translate=translate)
    diary.time_updated = datetime.now()
    diary.translated_content = translate_response.translated_text

    fs.collection('diary').document(diary.id).update(diary.dict(exclude={"id"}))
    return diary


def delete_diary(diary: DiaryDatabase, fs: Client):
    fs.collection('diary').document(diary.id).delete()
    return diary
