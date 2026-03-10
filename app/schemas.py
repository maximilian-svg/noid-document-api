from pydantic import BaseModel
from typing import Dict


class RenderRequest(BaseModel):
    template_name: str
    output_name: str
    tags: Dict[str, str]