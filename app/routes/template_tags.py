from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.payload_guard import extract_template_tags

router = APIRouter()


class TemplateTagsResponse(BaseModel):
    template_name: str
    tag_count: int
    tags: List[str]


@router.get("/template-tags/{template_name}", response_model=TemplateTagsResponse)
def get_template_tags(template_name: str):
    try:
        tags = extract_template_tags(template_name)
        return TemplateTagsResponse(
            template_name=template_name,
            tag_count=len(tags),
            tags=tags,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kunde inte läsa malltaggar: {e}")
