from pydantic import ValidationError

from app.schema.article import Article
from app.schema.diary import DiaryDatabase


def document_to_diary(docs):
    try:
        data = document_to_dict(docs)
        return DiaryDatabase(**data)
    except ValidationError:
        return None


def document_to_article(docs):
    try:
        data = document_to_dict(docs)
        return Article(**data)
    except ValidationError:
        return None


def document_to_dict(docs):
    data: dict = docs.to_dict()
    data["id"] = docs.id
    return data
