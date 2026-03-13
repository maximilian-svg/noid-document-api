from fastapi import APIRouter, HTTPException

from app.schemas import ValidateRequest, ValidateResponse
from app.services.payload_guard import validate_tags_json_against_template

router = APIRouter()


def _run_validation(request: ValidateRequest) -> ValidateResponse:
    try:
        result = validate_tags_json_against_template(
            template_name=request.template_name,
            tags_json=request.tags_json,
        )
        return ValidateResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Valideringsfel: {e}")


@router.post("/validate", response_model=ValidateResponse)
def validate_payload_legacy(request: ValidateRequest):
    return _run_validation(request)


@router.post("/validate-payload", response_model=ValidateResponse)
def validate_payload(request: ValidateRequest):
    return _run_validation(request)
