"""Scraping google dengan menggunakan serp API untuk mengambil artikel"""
from uuid import uuid4
from pydantic import BaseModel, parse_obj_as
from serpapi import GoogleSearch
import json
from app.database import get_fs
from app.schema.diary import EmotionCategory
from app.schema.article import Article, ArticleLanguage
from app.utils.firestore import document_to_article
from config import DefaultSettings, get_settings
from google.cloud.firestore import Client


settings: DefaultSettings = get_settings()
fs: Client = next(get_fs())


class SearchItem(BaseModel):
    emotion: EmotionCategory
    query: str


def do_google_search(search_item: SearchItem):
    params = {
        "q": search_item.query,
        "location": "Indonesia",
        "hl": "id",
        "gl": "id",
        "google_domain": "google.co.id",
        "num": 40,
        "api_key": "14b6a80da727717e29d19c8eb3f42b3743fb0bb845eec17b062874c90d5d78e0"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    organic_result = results["organic_results"]

    for res in organic_result:
        articles = Article(emotion=search_item.emotion, language=ArticleLanguage.ID, **res)
        id = str(uuid4())
        fs.collection("articles").document(id).set(articles.dict())


def main():
    search_items = [
        SearchItem(emotion=EmotionCategory.ANGER, query="solusi mengatasi marah"),
        SearchItem(emotion=EmotionCategory.FEAR, query="solusi mengatasi rasa takut")]
    for si in search_items:
        do_google_search(si)


if __name__ == "__main__":
    main()
