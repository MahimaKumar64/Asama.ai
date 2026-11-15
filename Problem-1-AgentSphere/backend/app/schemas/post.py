from pydantic import BaseModel, Field
from uuid import UUID


class PostCreateRequest(BaseModel):
    author_agent_id: UUID
    title: str = Field(min_length=2, max_length=255)
    content: str = Field(min_length=5)


class PostCreateResponse(BaseModel):
    id: str
    author_agent_id: str
    title: str
    message: str
