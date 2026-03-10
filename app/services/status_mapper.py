def to_status_symbol(value: str) -> str:
    if not value:
        return ""

    v = str(value).strip().lower()

    mapping = {
        "stabil": "🟢",
        "följ upp": "🟡",
        "följupp": "🟡",
        "atgarda": "🟠",
        "åtgärda": "🟠",
        "prioritet": "🔴",
        "1": "🟢",
        "2": "🟡",
        "3": "🟠",
        "4": "🔴",
        "normal": "🟢",
        "borderline": "🟡",
        "abnormal": "🟠",
        "critical": "🔴",
        "high": "🔴",
        "severe": "🔴",
    }

    return mapping.get(v, value)