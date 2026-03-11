from fastapi import FastAPI
from app.routes.validate import router as validate_router
from app.routes.render import router as render_router
from app.routes.template_tags import router as template_tags_router
from app.routes.generate_from_json import router as generate_from_json_router
from app.routes.download import router as download_router
from app.routes.template_map import router as template_map_router
from app.routes.required_tags import router as required_tags_router

app = FastAPI(title="NOID Document API")

app.include_router(validate_router, prefix="/validate", tags=["validate"])
app.include_router(render_router, prefix="/render", tags=["render"])
app.include_router(template_tags_router, prefix="/template-tags", tags=["template-tags"])
app.include_router(generate_from_json_router, prefix="/generate-from-json", tags=["generate-from-json"])
app.include_router(download_router, prefix="/download", tags=["download"])
app.include_router(template_map_router, prefix="/template-map", tags=["template-map"])
app.include_router(required_tags_router, prefix="/required-tags", tags=["required-tags"])

@app.get("/health")
def health():
    return {"ok": True}