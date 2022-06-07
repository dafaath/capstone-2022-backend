import os
import enum
import re
from datetime import datetime
from uuid import uuid4

import six
import pickle
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from fastapi import HTTPException
from google.cloud.firestore import Client
from google.cloud.translate_v2 import Client as TranslateClient
from tensorflow.keras.preprocessing.sequence import pad_sequences
from app.schema.diary import (CreateDiaryBody, DiaryDatabase, EmotionCategory,
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

def prediction(input: str):
    arrayInput = re.split('[?.!]', input)

    #Secara berurutan array dimulai dari kiri menghitung sad, joy, fear, love, surprise
    emotionPrediction = [0,0,0,0,0,0]

    tokenizer = None
    filename = 'tokenizer.pickle'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'utils', filename)
    with open(full_path_filename, 'rb') as x:
        tokenizer = pickle.load(x)
    tokenizedArrayInput = tokenizer.texts_to_sequences(arrayInput)
    paddedInput = pad_sequences(tokenizedArrayInput,padding="post",truncating="post",maxlen=400)

    filename = 'model.h5'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'utils', filename)
    model = tf.keras.models.load_model(full_path_filename)
    predictions = model.predict(paddedInput)

    for prediction in predictions:
        prediction = prediction.tolist()
        maxIndex = prediction.index(max(prediction))
        emotionPrediction[maxIndex] += 1

    emotion = emotionPrediction.index(max(emotionPrediction))
    if emotion == 0:
        return EmotionCategory.SADNESS
    elif emotion == 1:
        return EmotionCategory.JOY
    elif emotion == 2:
        return EmotionCategory.FEAR
    elif emotion == 3:
        return EmotionCategory.ANGER
    elif emotion == 4:
        return EmotionCategory.love
        
    return EmotionCategory.SURPRISE



def create_diary(
        input: CreateDiaryBody,
        user_id: str,
        fs: Client,
        translate_client: TranslateClient,
        translate: bool = True,
        emotion: EmotionCategory = None):

    if emotion is None:
        # TODO detect emotion
        emotion = prediction(input.content)

    translate_response = translate_content(input.content, translate_client, translate=translate)

    id = str(uuid4())
    time_created = datetime.now()
    time_updated = datetime.now()
    data = DiaryDatabase(
        id=id,
        title=input.title,
        content=input.content,
        translated_content=translate_response.translated_text,
        emotion=emotion,
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


def get_emotion_summary(diaries: list[DiaryDatabase]):
    emotion_freq = {}
    for diary in diaries:
        if diary.emotion not in emotion_freq:
            emotion_freq[diary.emotion] = 1
        else:
            emotion_freq[diary.emotion] += 1
    emotion = None
    max = 0
    for i, k in enumerate(emotion_freq):
        if i == 0 or emotion_freq[k] > max:
            max = emotion_freq[k]
            emotion = k
    return emotion


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
