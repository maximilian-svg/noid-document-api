from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.services.tag_extractor import extract_tags_from_docx

router = APIRouter()

TEMPLATE_DIR = Path("templates")

@router.get("/{template_name}")
def get_template_tags(template_name: str):
    template_path = TEMPLATE_DIR / template_name

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")

    tags = sorted(list(extract_tags_from_docx(str(template_path))))

    return {
        "template_name": template_name,
        "tag_count": len(tags),
        "tags": tags,
    }