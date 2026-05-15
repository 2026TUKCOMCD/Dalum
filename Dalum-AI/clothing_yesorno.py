import sys
import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from PIL import Image

CLOTHING_PROMPTS = [
    "a photo of clothing or fashion item",
    "a photo of a shirt, pants, dress, or jacket",
    "a photo of shoes, bag, or hat",
    "a product photo of apparel or accessory",
]

NOT_CLOTHING_PROMPTS = [
    "a photo of a landscape or nature scenery",
    "a photo of an animal or pet",
    "a photo of a map or diagram",
    "a photo of food or drink",
    "a photo of a person's face or portrait",
    "a photo of a building or architecture",
    "a photo of a document or text",
    "a photo of a vehicle or transportation",
    "this image does not contain clothing or fashion",
    "a photo of plants or trees",
]

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"디바이스: {device}")

model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model.eval()

def _get_text_emb(texts):
    inputs = processor(text=texts, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_text_features(**inputs)
    if not isinstance(out, torch.Tensor):
        out = out.pooler_output
    return F.normalize(out, dim=-1)

clothing_embs     = _get_text_emb(CLOTHING_PROMPTS)
not_clothing_embs = _get_text_emb(NOT_CLOTHING_PROMPTS)

def is_clothing(image_path: str) -> bool:
    image  = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        img_feats = model.get_image_features(**inputs)
    if not isinstance(img_feats, torch.Tensor):
        img_feats = img_feats.pooler_output
    img_emb = F.normalize(img_feats, dim=-1)

    cloth_sims     = (img_emb @ clothing_embs.T)[0].cpu().numpy()
    not_cloth_sims = (img_emb @ not_clothing_embs.T)[0].cpu().numpy()

    best_cloth     = float(cloth_sims.max())
    best_not_cloth = float(not_cloth_sims.max())

    print(f"  의류 유사도:   {best_cloth:.4f}  ({CLOTHING_PROMPTS[cloth_sims.argmax()]})")
    print(f"  비의류 유사도: {best_not_cloth:.4f}  ({NOT_CLOTHING_PROMPTS[not_cloth_sims.argmax()]})")

    return best_cloth > best_not_cloth

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 clothing_yesorno.py <이미지 경로>")
        sys.exit(1)

    result = is_clothing(sys.argv[1])
    if result:
        print("✅ 의류 이미지입니다.")
    else:
        print("❌ 의류 이미지가 아닙니다.")