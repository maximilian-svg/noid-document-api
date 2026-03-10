from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas import ValidateRequest, ValidateResponse
from app.services.tag_extractor import extract_tags_from_docx

router = APIRouter()

TEMPLATE_DIR = Path("templates")

@router.post("", response_model=ValidateResponse)
def validate(request: ValidateRequest):

    template_path = TEMPLATE_DIR / request.template_name

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")

    template_tags = extract_tags_from_docx(str(template_path))
    incoming_tags = set(request.tags.keys())

    missing_tags = sorted(list(template_tags - incoming_tags))
    unknown_tags = sorted(list(incoming_tags - template_tags))
    empty_tags = sorted([k for k,v in request.tags.items() if str(v).strip() == ""])

    ok = len(missing_tags) == 0 and len(empty_tags) == 0

    return ValidateResponse(
        ok=ok,
        missing_tags=missing_tags,
        unknown_tags=unknown_tags,
        empty_tags=empty_tags,
    )