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
        self.temperature = temperature  # 🔥 Temperature Scaling

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

    # 5-CROP
    def _generate_multi_crops(self, image: np.ndarray, crop_size=256):

        h, w = image.shape[:2]

        if h < crop_size or w < crop_size:
            crop_size = min(h, w)

        crops = []

        cx, cy = w // 2, h // 2
        half = crop_size // 2
        crops.append(image[cy-half:cy+half, cx-half:cx+half])

        crops.append(image[0:crop_size, 0:crop_size])
        crops.append(image[0:crop_size, w-crop_size:w])
        crops.append(image[h-crop_size:h, 0:crop_size])
        crops.append(image[h-crop_size:h, w-crop_size:w])

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