import logging
from typing import Optional

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)

STYLE_PROMPTS: dict[str, list[str]] = {
    "casual": [
        "a photo of a person wearing casual everyday clothing",
        "a person dressed in simple comfortable outfit",
        "someone wearing a t-shirt and jeans",
        "casual daily wear, relaxed fit clothing",
    ],
    "formal": [
        "a photo of a person wearing formal business attire",
        "a person in a professional suit and tie",
        "someone dressed in office wear, blazer and dress pants",
        "formal professional clothing, business dress code",
    ],
    "sporty": [
        "a photo of a person wearing athletic sportswear",
        "someone in gym clothes and running shoes",
        "a person dressed in activewear for training",
        "sporty outfit, moisture-wicking fabric, athletic wear",
    ],
    "street": [
        "a photo of a person wearing streetwear",
        "someone in oversized hoodie and cargo pants, urban style",
        "hip-hop fashion, bold graphics, baggy street clothing",
        "urban streetwear, sneakers and graphic tee",
    ],
    "vintage": [
        "a photo of a person wearing vintage retro clothing",
        "someone dressed in old school thrift store fashion",
        "retro style outfit, 80s 90s inspired clothing",
        "vintage aesthetic clothing, second-hand fashion look",
    ],
    "american_casual": [
        "a photo of a person wearing american preppy style",
        "someone in college campus outfit, varsity jacket",
        "denim and flannel, classic american casual look",
        "preppy american fashion, polo shirt and chinos",
    ],
}

STYLE_LABELS = list(STYLE_PROMPTS.keys())


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
        self._text_embeds = self._encode_style_prompts()

    def _encode_style_prompts(self) -> torch.Tensor:
        """스타일별 텍스트 임베딩 평균을 미리 계산 (shape: num_styles x dim)"""
        style_embeddings = []
        with torch.no_grad():
            for prompts in STYLE_PROMPTS.values():
                text_inputs = self.processor(text=prompts, return_tensors="pt", padding=True)
                text_features = self.model.get_text_features(**text_inputs).pooler_output
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                style_embeddings.append(text_features.mean(dim=0))
        text_embeds = torch.stack(style_embeddings)
        return text_embeds / text_embeds.norm(dim=-1, keepdim=True)

    def classify(self, image: Image.Image) -> str:
        """가장 높은 확률의 스타일 레이블 반환"""
        probs = self._get_probs(image)
        return STYLE_LABELS[probs.argmax().item()]

    def classify_with_scores(self, image: Image.Image) -> dict[str, float]:
        """스타일별 확률 딕셔너리 반환"""
        probs = self._get_probs(image)
        return {label: float(probs[i]) for i, label in enumerate(STYLE_LABELS)}

    def _get_probs(self, image: Image.Image) -> torch.Tensor:
        image_inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = self.model.get_image_features(**image_inputs).pooler_output
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        logits = (image_features @ self._text_embeds.T) * self.model.logit_scale.exp()
        return logits.softmax(dim=1)[0]
