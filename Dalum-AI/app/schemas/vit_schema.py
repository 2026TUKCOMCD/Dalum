from pydantic import BaseModel
from typing import Any

class VitRequest(BaseModel):
    s3Key: str

class DupeSearchWithImageRequest(BaseModel):
    s3_key: str       # S3 내 이미지 경로 (예: "user_upload/original/xxx.jpg")
    top_k: int = 10

class DupeSearchRequest(BaseModel):
    clip_embedding: list[float]          # 512-dim  (/embedding 응답값)
    clip_design_probs: list[float]       # 37-dim   (/embedding 응답값)
    embedding: dict[str, Any]            # {color: [...], shape: [...], material: {...}}
    major_category: str | None = None    # 대분류 필터 (예: "TOP") - None이면 전체 검색
    middle_category: str | None = None   # 중분류 필터 (예: "SWEATSHIRT") - None이면 대분류로 폴백
    lab_color: list[float] | None = None # CIE LAB 색상 [L, a, b] — 색상 게이트용
    top_k: int = 10