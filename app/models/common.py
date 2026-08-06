from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Citation(BaseSchema):
    file_id: str
    file_name: str
    page_number: int | None = None
    chunk_index: int | None = None
    score: float