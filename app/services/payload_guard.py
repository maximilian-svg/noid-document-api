from pathlib import Path
from app.services.tag_extractor import extract_tags_from_docx


SUPPLEMENT_ROWS = {
    1: ["SUPPLEMENT_1_NAME", "SUPPLEMENT_1_DOSAGE", "SUPPLEMENT_1_DURATION", "SUPPLEMENT_1_PURPOSE"],
    2: ["SUPPLEMENT_2_NAME", "SUPPLEMENT_2_DOSAGE", "SUPPLEMENT_2_DURATION", "SUPPLEMENT_2_PURPOSE"],
    3: ["SUPPLEMENT_3_NAME", "SUPPLEMENT_3_DOSAGE", "SUPPLEMENT_3_DURATION", "SUPPLEMENT_3_PURPOSE"],
    4: ["SUPPLEMENT_4_NAME", "SUPPLEMENT_4_DOSAGE", "SUPPLEMENT_4_DURATION", "SUPPLEMENT_4_PURPOSE"],
    5: ["SUPPLEMENT_5_NAME", "SUPPLEMENT_5_DOSAGE", "SUPPLEMENT_5_DURATION", "SUPPLEMENT_5_PURPOSE"],
    6: ["SUPPLEMENT_6_NAME", "SUPPLEMENT_6_DOSAGE", "SUPPLEMENT_6_DURATION", "SUPPLEMENT_6_PURPOSE"],
}

CLINIC_SUPPORT_GROUPS = [
    ["INTERVENTION_PLASMALJUS_PURPOSE"],
    ["INTERVENTION_PAPIMI_PURPOSE"],
    ["INTERVENTION_BIOFEEDBACK_PURPOSE"],
    ["INTERVENTION_OTHER_NAME", "INTERVENTION_OTHER_PURPOSE"],
]


def get_template_tags_for_template(template_name: str) -> list[str]:
    template_path = Path("templates") / template_name
    return sorted(list(extract_tags_from_docx(str(template_path))))


def _normalize_payload(template_tags: list[str], incoming_payload: dict) -> dict:
    payload = {}
    for tag in template_tags:
        value = incoming_payload.get(tag, "")
        payload[tag] = "" if value is None else str(value).strip()
    return payload


def _optional_empty_tags(template_set: set[str]) -> set[str]:
    optional_tags = set()

    for row_tags in SUPPLEMENT_ROWS.values():
        for tag in row_tags:
            if tag in template_set:
                optional_tags.add(tag)

    for group in CLINIC_SUPPORT_GROUPS:
        for tag in group:
            if tag in template_set:
                optional_tags.add(tag)

    return optional_tags


def _validate_exact_template_match(template_tags: list[str], incoming_payload: dict) -> list[str]:
    errors = []
    template_set = set(template_tags)
    payload_set = set(incoming_payload.keys())

    missing = sorted(list(template_set - payload_set))
    extra = sorted(list(payload_set - template_set))

    if missing:
        errors.append(f"Saknade taggar: {missing}")

    if extra:
        errors.append(f"Extra taggar: {extra}")

    if len(incoming_payload.keys()) != len(template_tags):
        errors.append(
            f"Fel antal nycklar: payload={len(incoming_payload.keys())} mall={len(template_tags)}"
        )

    return errors


def _validate_non_empty_required_tags(template_tags: list[str], payload: dict) -> list[str]:
    errors = []
    template_set = set(template_tags)
    optional_tags = _optional_empty_tags(template_set)

    for tag in template_tags:
        if tag in optional_tags:
            continue

        if payload.get(tag, "") == "":
            errors.append(f"Tom obligatorisk tagg: {tag}")

    return errors


def _validate_measurement_rows(template_tags: list[str], payload: dict) -> list[str]:
    errors = []
    template_set = set(template_tags)

    for tag in template_tags:
        if not tag.endswith("_RESULT"):
            continue

        base = tag[:-7]
        result_key = f"{base}_RESULT"
        status_key = f"{base}_STATUS"
        ref_key = f"{base}_REF"

        result_val = payload.get(result_key, "").strip()
        status_exists = status_key in template_set
        ref_exists = ref_key in template_set

        status_val = payload.get(status_key, "").strip() if status_exists else ""
        ref_val = payload.get(ref_key, "").strip() if ref_exists else ""

        if result_val and status_exists and not status_val:
            errors.append(f"STOPP: {base} har RESULT men saknar STATUS")

        if status_val and not result_val:
            errors.append(f"STOPP: {base} har STATUS men saknar RESULT")

        if result_val and ref_exists and not ref_val:
            errors.append(f"STOPP: {base} har RESULT men saknar REF")

    return errors


def _validate_supplement_rows(template_tags: list[str], payload: dict) -> list[str]:
    errors = []
    template_set = set(template_tags)

    for row_number, row_tags in SUPPLEMENT_ROWS.items():
        existing_tags = [tag for tag in row_tags if tag in template_set]
        if not existing_tags:
            continue

        filled = [tag for tag in existing_tags if payload.get(tag, "").strip() != ""]

        if filled and len(filled) != len(existing_tags):
            errors.append(
                f"STOPP: tillskottsrad {row_number} är halvfylld. Fyllda fält: {filled}"
            )

    return errors


def _validate_clinic_support_rows(template_tags: list[str], payload: dict) -> list[str]:
    errors = []
    template_set = set(template_tags)

    for group in CLINIC_SUPPORT_GROUPS:
        existing_tags = [tag for tag in group if tag in template_set]
        if not existing_tags:
            continue

        filled = [tag for tag in existing_tags if payload.get(tag, "").strip() != ""]

        if filled and len(filled) != len(existing_tags):
            errors.append(
                f"STOPP: klinikstödsrad är halvfylld. Fyllda fält: {filled}"
            )

    return errors


def validate_payload_against_template(template_name: str, incoming_payload: dict):
    template_tags = get_template_tags_for_template(template_name)

    errors = []
    errors.extend(_validate_exact_template_match(template_tags, incoming_payload))

    payload = _normalize_payload(template_tags, incoming_payload)

    errors.extend(_validate_non_empty_required_tags(template_tags, payload))
    errors.extend(_validate_measurement_rows(template_tags, payload))
    errors.extend(_validate_supplement_rows(template_tags, payload))
    errors.extend(_validate_clinic_support_rows(template_tags, payload))

    if errors:
        raise Exception(
            "STOPP: Payloaden är inte en fullständig 1:1-spegel av mallens tagglista.\n"
            + "\n".join(errors)
        )

    return payload, template_tags