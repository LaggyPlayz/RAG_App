from pydantic import Field

from app.models.common import BaseSchema, Citation


class SearchRequest(BaseSchema):
    query: str = Field(..., min_length=1)
    knowledge_base_ids: list[str] = Field(default_factory=list)
    top_k: int | None = Field(default=None, ge=1, le=50)


class SearchResultItem(Citation):
    content: str


class SearchResponse(BaseSchema):
    query: str
    results: list[SearchResultItem]