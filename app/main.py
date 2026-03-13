from fastapi import FastAPI

app = FastAPI(title="NOID Document API")


def safe_include(module_path: str, tag: str, prefix: str = "") -> None:
    try:
        module = __import__(module_path, fromlist=["router"])
        app.include_router(module.router, prefix=prefix, tags=[tag])
        print(f"Loaded router: {module_path}")
    except Exception as e:
        print(f"Skipped router {module_path}: {e}")


for module_path, tag, prefix in [
    ("app.routes.render", "render", "/render"),
    ("app.routes.validate", "validate", ""),
    ("app.routes.template_map", "template-map", "/template-map"),
    ("app.routes.required_tags", "required-tags", ""),
    ("app.routes.template_tags", "template-tags", ""),
    ("app.routes.generate_from_json", "generate-from-json", "/generate-from-json"),
    ("app.routes.download", "download", ""),
]:
    safe_include(module_path, tag, prefix)


@app.get("/health")
def health():
    return {"ok": True}
