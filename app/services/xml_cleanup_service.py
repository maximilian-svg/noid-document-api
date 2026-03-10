import re
import zipfile
import tempfile
import shutil
import os

TAG_RE = re.compile(r"\{\{.*?\}\}")

def remove_leftover_tags_from_xml(docx_path: str) -> str:
    temp_dir = tempfile.mkdtemp()

    try:
        with zipfile.ZipFile(docx_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    cleaned = TAG_RE.sub("", content)

                    if cleaned != content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(cleaned)

        temp_docx = docx_path + ".tmp"

        with zipfile.ZipFile(temp_docx, "w", zipfile.ZIP_DEFLATED) as zip_out:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zip_out.write(full_path, arcname)

        shutil.move(temp_docx, docx_path)
        return docx_path

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)