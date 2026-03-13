from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    template_name: str
    output_name: str
    tags: Dict[str, str] = Field(default_factory=dict)


class RenderResponse(BaseModel):
    ok: bool
    output_path: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    leftover_xml_files: List[str] = Field(default_factory=list)
    leftover_tags: Dict[str, Any] = Field(default_factory=dict)


class GenerateStringRequest(BaseModel):
    template_name: str
    output_name: str
    tags_json: str


class ValidateRequest(BaseModel):
    template_name: str
    tags_json: str


class ValidateResponse(BaseModel):
    ok: bool
    errors: List[str] = Field(default_factory=list)
    template_name: Optional[str] = None
    tag_count: int = 0
    filled_tag_count: int = 0
    result_count: int = 0
    status_count: int = 0
    comment_count: int = 0
