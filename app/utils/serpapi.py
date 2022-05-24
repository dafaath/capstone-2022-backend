from typing import Any, Dict, List, Optional

from app.utils.schema import TemplateModel


class AnswerBox(TemplateModel):
    type: str
    title: str
    link: str
    displayed_link: str
    date: str
    snippet: str
    list: List[str]
    thumbnail: str
    people_also_search_for: List[Any]


class DetectedExtensions(TemplateModel):
    skor: Optional[float]
    suara: Optional[int]
    langkah: Optional[int]


class Top(TemplateModel):
    detected_extensions: DetectedExtensions
    extensions: List[str]


class RichSnippet(TemplateModel):
    top: Top


class OrganicResult(TemplateModel):
    position: int
    title: str
    link: str
    displayed_link: str
    snippet: Optional[str]
    snippet_highlighted_words: Optional[List[str]]
    date: Optional[str]
    rich_snippet: Optional[RichSnippet]


class Pagination(TemplateModel):
    current: int
    next: str
    other_pages: Dict[str, str]
    next_link: Optional[str]


class RelatedQuestion(TemplateModel):
    question: str
    title: str
    link: str
    list: Optional[List[str]]
    displayed_link: str
    snippet: Optional[str]


class RelatedSearch(TemplateModel):
    query: str
    link: str


class SearchInformation(TemplateModel):
    organic_results_state: str
    query_displayed: str
    total_results: int
    time_taken_displayed: float


class SearchMetadata(TemplateModel):
    id: str
    status: str
    json_endpoint: str
    created_at: str
    processed_at: str
    google_url: str
    raw_html_file: str
    total_time_taken: float


class SearchParameters(TemplateModel):
    engine: str
    q: str
    location_requested: str
    location_used: str
    google_domain: str
    hl: str
    gl: str
    device: str


class SearchResponse(TemplateModel):
    search_metadata: SearchMetadata
    search_parameters: SearchParameters
    search_information: SearchInformation
    related_questions: List[RelatedQuestion]
    answer_box: AnswerBox
    organic_results: List[OrganicResult]
    related_searches: List[RelatedSearch]
    pagination: Pagination
    serpapi_pagination: Pagination
