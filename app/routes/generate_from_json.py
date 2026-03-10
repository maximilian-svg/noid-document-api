from fastapi import APIRouter, HTTPException, Request
from pathlib import Path

from app.schemas import RenderRequest, RenderResponse
from app.services.docx_renderer import render_docx
from app.services.postcheck_service import run_postcheck
from app.services.xml_cleanup_service import remove_leftover_tags_from_xml
from app.services.report_rules import run_report_rules

router = APIRouter()

@router.post("", response_model=RenderResponse)
def generate_from_json(request: Request, payload: RenderRequest):
    template_path = Path("templates") / payload.template_name

    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        output_path = render_docx(
            template_name=payload.template_name,
            output_name=payload.output_name,
            tag_map=payload.tags,
        )

        output_path = remove_leftover_tags_from_xml(output_path)
        postcheck = run_postcheck(output_path)
        rule_errors = run_report_rules(output_path, payload.tags)

        if not postcheck["ok"] or rule_errors:
            return RenderResponse(
                ok=False,
                output_path=None,
                errors=postcheck["errors"] + rule_errors,
                leftover_xml_files=postcheck["leftover_xml_files"],
                leftover_tags=postcheck["leftover_tags"],
            )

        filename = Path(output_path).name
        download_url = str(request.base_url).rstrip("/") + f"/download/{filename}"

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