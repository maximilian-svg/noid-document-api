from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TemplateMapResponse(BaseModel):
    bas: str
    fokus: str
    optimal: str
    aterbesok: str


@router.get("/template-map", response_model=TemplateMapResponse)
def get_template_map():
    return TemplateMapResponse(
        bas="NOID_Rapportmall_Bas_Maskinfyllbar_v13.docx",
        fokus="",
        optimal="",
        aterbesok="",
    )
