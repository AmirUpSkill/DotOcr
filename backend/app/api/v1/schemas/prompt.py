from pydantic import BaseModel

class PromptDto(BaseModel):
    id: str
    name: str
    description: str

class PromptListResponse(BaseModel):
    prompts: list[PromptDto]