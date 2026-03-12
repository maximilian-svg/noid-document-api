def normalize_status_to_symbol(value: str) -> str:
    if value is None:
        return ""

    v = str(value).strip().lower()

    mapping = {
        "1": "🟢",
        "2": "🟡",
        "3": "🟠",
        "4": "🔴",
        "normal": "🟢",
        "borderline": "🟡",
        "abnormal": "🟠",
        "high": "🔴",
        "critical": "🔴",
        "severe": "🔴",
        "stabil": "🟢",
        "följ upp": "🟡",
        "åtgärda": "🟠",
        "prioritet": "🔴",
    }

    return mapping.get(v, value)