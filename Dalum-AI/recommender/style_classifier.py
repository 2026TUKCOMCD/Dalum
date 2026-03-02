import logging
from typing import Optional

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)

STYLE_PROMPTS: dict[str, str] = {
    "casual":           "casual everyday clothing, simple comfortable outfit, t-shirt and jeans",
    "formal":           "formal business attire, professional dress, suit blazer office wear",
    "sporty":           "sporty athletic wear, gym clothes, activewear training outfit",
    "street":           "streetwear urban style, oversized hoodie, bold graphics hip-hop fashion",
    "vintage":          "vintage retro style clothing, old school fashion thrift store look",
    "american_casual":  "american casual preppy style, college look, denim flannel varsity",
}

STYLE_LABELS = list(STYLE_PROMPTS.keys())
STYLE_TEXTS  = list(STYLE_PROMPTS.values())


class StyleClassifier:
    """
    CLIP 기반 zero-shot 스타일 분류기.
    제품 이미지를 입력받아 스타일 태그를 반환한다.
    학습 데이터 없이 동작하므로 DB 내 모든 제품에 일괄 적용 가능.

    Usage:
        classifier = StyleClassifier()
        style = classifier.classify(pil_image)           # e.g. "casual"
        scores = classifier.classify_with_scores(img)   # 전체 확률 반환
    """

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        logger.info(f"StyleClassifier 로딩: {model_name}")
        self.model     = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

    def classify(self, image: Image.Image) -> str:
        """가장 높은 확률의 스타일 레이블 반환"""
        probs = self._get_probs(image)
        return STYLE_LABELS[probs.argmax().item()]

    def classify_with_scores(self, image: Image.Image) -> dict[str, float]:
        """스타일별 확률 딕셔너리 반환"""
        probs = self._get_probs(image)
        return {label: float(probs[i]) for i, label in enumerate(STYLE_LABELS)}

    def _get_probs(self, image: Image.Image) -> torch.Tensor:
        inputs = self.processor(
            text=STYLE_TEXTS,
            images=image,
            return_tensors="pt",
            padding=True,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.logits_per_image.softmax(dim=1)[0]
