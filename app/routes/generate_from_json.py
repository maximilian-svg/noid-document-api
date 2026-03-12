import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.schemas import GenerateStringRequest, RenderResponse
from app.services.docx_renderer import render_docx
from app.services.postcheck_service import run_postcheck
from app.services.xml_cleanup_service import remove_leftover_tags_from_xml
from app.services.report_rules import run_report_rules
from app.services.status_mapper import normalize_status_to_symbol
from app.services.payload_guard import validate_payload_against_template

router = APIRouter()

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "https://noid-document-api.onrender.com"
)


@router.post("", response_model=RenderResponse)
def generate_from_json(payload: GenerateStringRequest):
    template_path = Path("templates") / payload.template_name

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        try:
            tags = json.loads(payload.tags_json)
        except Exception:
            return RenderResponse(
                ok=False,
                output_path=None,
                errors=["Invalid tags_json: must be valid JSON string"],
                leftover_xml_files=[],
                leftover_tags={},
            )

        if not isinstance(tags, dict):
            return RenderResponse(
                ok=False,
                output_path=None,
                errors=["Invalid tags_json: must decode to an object/dictionary"],
                leftover_xml_files=[],
                leftover_tags={},
            )

        normalized_tags = {}
        for key, value in tags.items():
            key_str = str(key)
            value_str = "" if value is None else str(value).strip()

            if key_str.endswith("_STATUS") and value_str:
                value_str = normalize_status_to_symbol(value_str)

            normalized_tags[key_str] = value_str

        # HÅRD 1:1-SPÄRR MOT MALLEN
        validated_payload, template_tags = validate_payload_against_template(
            payload.template_name,
            normalized_tags,
        )

        output_path = render_docx(
            template_name=payload.template_name,
            output_name=payload.output_name,
            tag_map=validated_payload,
        )

        output_path = remove_leftover_tags_from_xml(output_path)

        postcheck = run_postcheck(output_path)
        rule_errors = run_report_rules(output_path, validated_payload)

        if not postcheck["ok"] or rule_errors:
            return RenderResponse(
                ok=False,
                output_path=None,
                errors=postcheck["errors"] + rule_errors,
                leftover_xml_files=postcheck["leftover_xml_files"],
                leftover_tags=postcheck["leftover_tags"],
            )

        filename = Path(output_path).name
        download_url = f"{PUBLIC_BASE_URL}/download/{filename}"

        return RenderResponse(
            ok=True,
            output_path=download_url,
            errors=[],
            leftover_xml_files=[],
            leftover_tags={},
        )

    except Exception as e:
        return RenderResponse(
            ok=False,
            output_path=None,
            errors=[str(e)],
            leftover_xml_files=[],
            leftover_tags={},
        )