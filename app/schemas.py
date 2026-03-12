from pydantic import BaseModel
from typing import Dict, List, Optional


class ValidateRequest(BaseModel):
    report_type: str
    template_name: str
    tags: Dict[str, str]


class ValidateResponse(BaseModel):
    ok: bool
    missing_tags: List[str]
    unknown_tags: List[str]
    empty_tags: List[str]


class RenderRequest(BaseModel):
    template_name: str
    output_name: str
    tags: Dict[str, str]


class GenerateStringRequest(BaseModel):
    template_name: str
    output_name: str
    tags_json: str


class RenderResponse(BaseModel):
    ok: bool
    output_path: Optional[str] = None
    errors: List[str] = []
    leftover_xml_files: List[str] = []
    leftover_tags: Dict[str, List[str]] = {}