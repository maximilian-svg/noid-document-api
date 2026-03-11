from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.services.tag_extractor import extract_tags_from_docx

router = APIRouter()

TEMPLATE_DIR = Path("templates")

COMMON_REQUIRED_TAGS = {
    "CLIENT_NAME",
    "REPORT_DATE",
    "REPORT_TYPE",
    "OVERVIEW_STRENGTHS",
    "OVERVIEW_FOCUS_AREA",
    "OVERVIEW_GOALS",
    "WELLNESS_INDEX_TREND",
    "TEST_SUMMARY",
    "DIET_RECOMMENDATIONS_SHORT",
    "SUPPLEMENT_PLAN_SHORT",
    "CURRENT_STATUS_AND_PURPOSE"
}

@router.get("/{template_name}")
def get_required_tags(template_name: str):
    template_path = TEMPLATE_DIR / template_name

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")

    template_tags = set(extract_tags_from_docx(str(template_path)))
    required_tags = sorted(list(template_tags.intersection(COMMON_REQUIRED_TAGS)))

    return {
        "template_name": template_name,
        "required_tag_count": len(required_tags),
        "required_tags": required_tags
    }