import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"
TAG_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

OPTIONAL_ROW_PREFIXES = (
    "SUPPLEMENT_",
    "TILLSKOTT_",
    "CLINIC_SUPPORT_",
    "KLINIKSTOD_",
    "KLINIKSTÖD_",
)


def _normalize(value: str) -> str:
    return (
        value.upper()
        .replace("Å", "A")
        .replace("Ä", "A")
        .replace("Ö", "O")
    )


def load_tags_json(tags_json: str) -> Dict[str, str]:
    try:
        data = json.loads(tags_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"tags_json är inte giltig JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError("tags_json måste innehålla ett JSON-objekt.")

    cleaned: Dict[str, str] = {}
    for key, value in data.items():
        cleaned[str(key)] = "" if value is None else str(value).strip()
    return cleaned


def extract_template_tags(template_name: str) -> List[str]:
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Mallen finns inte: {template_path}")

    tags = set()
    with zipfile.ZipFile(template_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".xml"):
                text = zf.read(name).decode("utf-8", errors="ignore")
                for match in TAG_RE.findall(text):
                    tags.add(match)

    return sorted(tags)


def _optional_row_key(tag: str) -> Optional[str]:
    normalized = _normalize(tag)
    row_numbers = re.findall(r"\d+", normalized)
    if not row_numbers:
        return None

    for prefix in OPTIONAL_ROW_PREFIXES:
        if prefix in normalized:
            return f"{prefix}{row_numbers[0]}"
    return None


def validate_tags_json_against_template(template_name: str, tags_json: str) -> Dict[str, object]:
    payload = load_tags_json(tags_json)
    template_tags = extract_template_tags(template_name)

    errors: List[str] = []

    missing_keys = sorted(set(template_tags) - set(payload.keys()))
    extra_keys = sorted(set(payload.keys()) - set(template_tags))

    if missing_keys:
        errors.append("Payload saknar malltaggar: " + ", ".join(missing_keys[:25]))
    if extra_keys:
        errors.append("Payload innehåller okända taggar: " + ", ".join(extra_keys[:25]))

    optional_groups = defaultdict(list)

    filled_tag_count = 0
    result_count = 0
    status_count = 0
    comment_count = 0

    for tag in template_tags:
        value = payload.get(tag, "").strip()

        if value:
            filled_tag_count += 1

        if "{{" in value or "}}" in value:
            errors.append(f"Värdet för {tag} innehåller kvarvarande malltagg.")

        row_key = _optional_row_key(tag)
        if row_key:
            optional_groups[row_key].append((tag, value))
        else:
            if value == "":
                errors.append(f"Obligatorisk tagg är tom: {tag}")

        if tag.endswith("_RESULT") and value:
            result_count += 1

        if tag.endswith("_STATUS") and value:
            status_count += 1

        if tag.startswith("COMMENT_") and value:
            comment_count += 1

    for row_key, row_items in optional_groups.items():
        filled = [tag for tag, value in row_items if value]
        empty = [tag for tag, value in row_items if not value]

        if filled and empty:
            errors.append(
                f"Halvfylld städbar rad ({row_key}). Fyllda: {', '.join(filled)} | Tomma: {', '.join(empty)}"
            )

    for tag in template_tags:
        value = payload.get(tag, "").strip()

        if tag.endswith("_RESULT") and value:
            base = tag[:-7]
            status_tag = f"{base}_STATUS"
            ref_tag = f"{base}_REF"

            if status_tag in template_tags and not payload.get(status_tag, "").strip():
                errors.append(f"{tag} har värde men {status_tag} saknas.")

            if ref_tag in template_tags and not payload.get(ref_tag, "").strip():
                errors.append(f"{tag} har värde men {ref_tag} saknas.")

        if tag.endswith("_STATUS") and value:
            result_tag = f"{tag[:-7]}_RESULT"
            if result_tag in template_tags and not payload.get(result_tag, "").strip():
                errors.append(f"{tag} har värde men {result_tag} saknas.")

        if tag.endswith("_REF") and value:
            result_tag = f"{tag[:-4]}_RESULT"
            if result_tag in template_tags and not payload.get(result_tag, "").strip():
                errors.append(f"{tag} har värde men {result_tag} saknas.")

    if result_count == 0:
        errors.append("Minst ett ..._RESULT måste vara ifyllt före generering.")

    deduped_errors = []
    seen = set()
    for err in errors:
        if err not in seen:
            deduped_errors.append(err)
            seen.add(err)

    return {
        "ok": len(deduped_errors) == 0,
        "errors": deduped_errors,
        "template_name": template_name,
        "tag_count": len(template_tags),
        "filled_tag_count": filled_tag_count,
        "result_count": result_count,
        "status_count": status_count,
        "comment_count": comment_count,
    }


def validate_payload_against_template(
    template_name: Optional[str] = None,
    tags_json: Optional[str] = None,
    payload: Optional[Dict[str, str]] = None,
    *args,
    **kwargs,
) -> Dict[str, object]:
    if template_name is None and len(args) >= 1:
        template_name = args[0]

    if tags_json is None and len(args) >= 2 and isinstance(args[1], str):
        possible_json = args[1]
        if possible_json.strip().startswith("{"):
            tags_json = possible_json

    if payload is None:
        payload = kwargs.get("payload") or kwargs.get("tags")

    if payload is None and len(args) >= 2 and isinstance(args[1], dict):
        payload = args[1]

    if template_name is None:
        raise ValueError("template_name saknas i validate_payload_against_template.")

    if tags_json is None:
        if payload is None:
            raise ValueError("Antingen tags_json eller payload måste skickas.")
        tags_json = json.dumps(payload, ensure_ascii=False)

    return validate_tags_json_against_template(template_name, tags_json)
