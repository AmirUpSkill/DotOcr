from fastapi import APIRouter
from app.api.v1.endpoints import prompts, parse

api_router = APIRouter()

api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(parse.router, prefix="/parse", tags=["Parsing"])