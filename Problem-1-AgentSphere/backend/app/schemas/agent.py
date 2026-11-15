from pydantic import BaseModel, HttpUrl, Field


class AgentRegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    industry_category: str = Field(min_length=2, max_length=100)
    webhook_url: HttpUrl
    interest_manifesto: str = Field(min_length=10)


class AgentRegisterResponse(BaseModel):
    id: str
    company_name: str
    industry_category: str
    message: str
