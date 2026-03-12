SECTION_PREFIXES = {
    "Lifestyle": ["LIFESTYLE_"],
    "HRV": ["HRV_", "EMOTIONAL_"],
    "GSR": ["GSR_"],
    "Vascular": ["VASCULAR_"],
}

def _belongs_to_section(tag: str, prefixes: list[str]) -> bool:
    return any(tag.startswith(prefix) for prefix in prefixes)

def validate_half_filled_rows(tags: dict) -> list[str]:
    errors = []

    base_names = set()
    for key in tags.keys():
        if key.endswith("_RESULT"):
            base_names.add(key[:-7])
        elif key.endswith("_STATUS"):
            base_names.add(key[:-7])
        elif key.endswith("_REF"):
            base_names.add(key[:-4])

    for base in sorted(base_names):
        result_key = f"{base}_RESULT"
        status_key = f"{base}_STATUS"
        ref_key = f"{base}_REF"

        result_val = str(tags.get(result_key, "")).strip()
        status_val = str(tags.get(status_key, "")).strip()
        ref_val = str(tags.get(ref_key, "")).strip()

        if result_val and not status_val:
            errors.append(f"Half-filled row: {result_key} has value but {status_key} is empty")

        if status_val and not result_val:
            errors.append(f"Half-filled row: {status_key} has value but {result_key} is empty")

        # REF är inte alltid obligatorisk, så här flaggar vi bara om ref-tagg finns och du senare vill skärpa regeln
        if ref_key in tags and result_val and not ref_val:
            errors.append(f"REF missing for populated row: {ref_key}")

    return errors

def validate_section_coverage(tags: dict) -> dict:
    coverage = {}

    for section, prefixes in SECTION_PREFIXES.items():
        result_keys = [
            key for key in tags.keys()
            if key.endswith("_RESULT") and _belongs_to_section(key, prefixes)
        ]

        filled = sum(1 for key in result_keys if str(tags.get(key, "")).strip())
        total = len(result_keys)

        coverage[section] = {
            "filled": filled,
            "total": total,
        }

    return coverage

def coverage_errors(coverage: dict, min_ratio: float = 0.5) -> list[str]:
    errors = []

    for section, data in coverage.items():
        total = data["total"]
        filled = data["filled"]

        if total == 0:
            continue

        ratio = filled / total

        if 0 < ratio < min_ratio:
            errors.append(
                f"Section coverage too low: {section} {filled}/{total}"
            )

    return errors