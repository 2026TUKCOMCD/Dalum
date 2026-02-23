from fastapi import FastAPI
from vit.runners.run_upload_vit import process_upload_image

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "AI server running"}

@app.post("/process")
def process_image(s3_key: str, category: str = None):
    result = process_upload_image(s3_key, category)
    return result