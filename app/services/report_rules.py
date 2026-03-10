import zipfile

REQUIRED_TAGS = [
    "CLIENT_NAME",
    "CURRENT_STATUS_AND_PURPOSE",
    "OVERVIEW_GOALS",
]

def check_required_tags(tag_map: dict) -> list:
    errors = []

    for tag in REQUIRED_TAGS:
        if tag not in tag_map or str(tag_map[tag]).strip() == "":
            errors.append(f"Required field missing: {tag}")

    return errors


def check_logo_exists(docx_path: str) -> list:
    errors = []

    with zipfile.ZipFile(docx_path, "r") as z:
        media_files = [f for f in z.namelist() if f.startswith("word/media/")]

        if len(media_files) == 0:
            errors.append("No images found in document (logo missing)")

    return errors


def check_client_name_in_document(docx_path: str, client_name: str) -> list:
    errors = []

    with zipfile.ZipFile(docx_path, "r") as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

        if client_name not in xml:
            errors.append("Client name not found in report")

    return errors


def run_report_rules(docx_path: str, tag_map: dict) -> list:
    errors = []

    errors += check_required_tags(tag_map)
    errors += check_logo_exists(docx_path)

    if "CLIENT_NAME" in tag_map:
        errors += check_client_name_in_document(docx_path, tag_map["CLIENT_NAME"])

    return errors