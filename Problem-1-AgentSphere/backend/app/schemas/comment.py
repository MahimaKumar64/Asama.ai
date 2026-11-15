from pydantic import BaseModel, Field
from uuid import UUID


class CommentCreateRequest(BaseModel):
    author_agent_id: UUID
    content: str = Field(min_length=1)


class CommentCreateResponse(BaseModel):
    id: str
    post_id: str
    author_agent_id: str
    content: str
    message: str
