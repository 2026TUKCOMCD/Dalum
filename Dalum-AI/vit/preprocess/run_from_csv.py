import csv
import os
from vit.preprocess.utils.image_loader import load_image_from_url
from vit.preprocess.background_clothing import BackgroundClothingPipeline

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(BASE_DIR, "..", "Dalum-CR", "final", ".csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "vit", "outputs", "preprocess", "clothing_images")

pipeline = BackgroundClothingPipeline()
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run():
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            image = load_image_from_url(row["이미지 URL"])
            out = os.path.join(OUTPUT_DIR, f"{i:08d}.png")

            pipeline.process(
                image=image,
                main=row["대분류"],
                sub=row["중분류"],
                category=row["카테고리"],
                output_path=out
            )

if __name__ == "__main__":
    run()