import zipfile
import re

TAG_RE = re.compile(r"\{\{(.*?)\}\}")

def find_leftover_tags(docx_path: str) -> dict:
    leftovers = {}

    with zipfile.ZipFile(docx_path, "r") as z:
        for name in z.namelist():
            if name.endswith(".xml"):
                content = z.read(name).decode("utf-8", errors="ignore")
                matches = TAG_RE.findall(content)
                if matches:
                    leftovers[name] = sorted(list(set(matches)))

    return leftovers


def inspect_docx_structure(docx_path: str) -> dict:
    with zipfile.ZipFile(docx_path, "r") as z:
        names = set(z.namelist())

        headers = [n for n in names if n.startswith("word/header")]
        media = [n for n in names if n.startswith("word/media/")]

        return {
            "has_headers": len(headers) > 0,
            "media_count": len(media),
            "headers": headers,
            "media_files": media,
        }


def run_postcheck(docx_path: str) -> dict:
    leftover_map = find_leftover_tags(docx_path)
    structure = inspect_docx_structure(docx_path)

    errors = []

    if leftover_map:
        files = ", ".join(leftover_map.keys())
        errors.append(f"Leftover tags found in: {files}")

    if not structure["has_headers"]:
        errors.append("No header files found in DOCX")

    if structure["media_count"] == 0:
        errors.append("No media files found in DOCX")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "leftover_xml_files": list(leftover_map.keys()),
        "leftover_tags": leftover_map,
        "structure": structure,
    }