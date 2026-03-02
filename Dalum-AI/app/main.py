#서버 진입점
from fastapi import FastAPI
from app.api.vit_router import router as vit_router
from app.api.styling_recommend import router as styling_router

app = FastAPI()

app.include_router(vit_router, prefix="/api/v1/vit")
app.include_router(styling_router, prefix="/api/v1/styling")

@app.get("/")
def health_check():
    return {"status": "AI server running"}