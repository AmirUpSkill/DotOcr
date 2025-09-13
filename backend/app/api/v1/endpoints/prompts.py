from fastapi import APIRouter, HTTPException
from app.prompts.definitions import load_prompts
from app.api.v1.schemas.prompt import PromptListResponse, PromptDto

router = APIRouter()

@router.get(
    "/",
    response_model=PromptListResponse,
    summary="List Available Prompts",
    description="Retrieves the list of predefined prompts that can be used for OCR processing."
)
def list_available_prompts():
    """
    Handles the GET request to list all available prompts.
    """
    try:
        prompts_data = load_prompts()
        prompt_dtos = [PromptDto(**p) for p in prompts_data]
        return PromptListResponse(prompts=prompt_dtos)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load prompts: {e}"
        )