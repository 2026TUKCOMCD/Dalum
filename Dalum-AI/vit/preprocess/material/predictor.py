import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import cv2
import timm
import numpy as np

from vit.preprocess.material.classes import IDX_TO_CLASS


class MaterialPredictor:
    def __init__(self, weight_path, temperature=0.7):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.temperature = temperature 

        self.model = timm.create_model(
            "vit_tiny_patch16_224",
            pretrained=False,
            num_classes=33
        )

        checkpoint = torch.load(weight_path, map_location=self.device)
        state_dict = checkpoint["model"] if "model" in checkpoint else checkpoint

        cleaned_state_dict = {}
        for k, v in state_dict.items():
            if k.startswith("module."):
                cleaned_state_dict[k.replace("module.", "")] = v
            else:
                cleaned_state_dict[k] = v

        self.model.load_state_dict(cleaned_state_dict, strict=True)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def _generate_multi_crops(self, image: np.ndarray, crop_size: int = 256):
        h, w = image.shape[:2]
        crop_size = min(crop_size, h, w)
        half = crop_size // 2

        # 배경 분리: 세그멘테이션 후 이미지는 배경이 검정(≈0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fg_mask = gray > 10
        rows = np.where(fg_mask.any(axis=1))[0]
        cols = np.where(fg_mask.any(axis=0))[0]

        if len(rows) == 0 or len(cols) == 0:
            fy1, fy2, fx1, fx2 = 0, h, 0, w
        else:
            fy1, fy2 = int(rows[0]), int(rows[-1])
            fx1, fx2 = int(cols[0]), int(cols[-1])

        fg_cy = (fy1 + fy2) // 2
        fg_cx = (fx1 + fx2) // 2
        fg_h  = max(1, fy2 - fy1)
        fg_w  = max(1, fx2 - fx1)

        def safe_crop(cy, cx):
            y1 = max(0, min(h - crop_size, cy - half))
            x1 = max(0, min(w - crop_size, cx - half))
            return image[y1:y1 + crop_size, x1:x1 + crop_size]

        crops = [
            safe_crop(fg_cy,                   fg_cx),               # 전경 중앙
            safe_crop(fy1 + fg_h // 4,         fg_cx),               # 상단 (칼라/어깨 질감)
            safe_crop(fy1 + fg_h * 3 // 4,     fg_cx),               # 하단 (헴 질감)
            safe_crop(fg_cy,                   fx1 + fg_w // 4),     # 좌측 소매
            safe_crop(fg_cy,                   fx1 + fg_w * 3 // 4), # 우측 소매
        ]
        return crops

    # Multi-crop + Temperature Scaling
    def predict_from_array(self, image_array):

        crops = self._generate_multi_crops(image_array)

        prob_list = []

        with torch.no_grad():
            for crop in crops:
                image_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image_rgb)

                tensor = self.transform(image).unsqueeze(0).to(self.device)

                logits = self.model(tensor)

                # Temperature Scaling 적용
                logits = logits / self.temperature

                probs = F.softmax(logits, dim=1)[0]
                prob_list.append(probs.cpu().numpy())

        # 5-crop 평균
        mean_probs = np.mean(prob_list, axis=0)

        # 33차원 material embedding (softmax 분포)
        material_vector = {
            IDX_TO_CLASS[i]: float(mean_probs[i])
            for i in range(len(IDX_TO_CLASS))
        }

        # Top-3 추출
        top3_idx = np.argsort(mean_probs)[-3:][::-1]

        top3 = [
            (IDX_TO_CLASS[i], float(mean_probs[i]))
            for i in top3_idx
        ]

        return top3, material_vector