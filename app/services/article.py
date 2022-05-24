
from google.cloud.firestore import Client

from app.schema.diary import EmotionCategory
from app.utils.firestore import document_to_article


def get_all_articles(fs: Client, page: int = None, size: int = None, emotions: list[EmotionCategory] = None):
    ref = fs.collection('articles')

    if emotions:
        emotions = list(map(lambda x: x.value, emotions))
        ref = ref.where("emotion", "in", emotions)
    else:
        ref = ref.order_by("emotion")

    ref = ref.order_by("position")

    if page and size:
        offset = (page - 1) * size
        ref = ref.limit(size).offset(offset)

    documents = ref.get()
    diaries = [document_to_article(docs) for docs in documents if document_to_article(docs) is not None]
    return diaries
