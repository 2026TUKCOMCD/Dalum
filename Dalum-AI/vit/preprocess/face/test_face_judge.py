import cv2
import os

from vit.preprocess.face.face_detector import FaceDetector
from vit.preprocess.face.face_judge import has_real_face
from vit.preprocess.face.face_index import FaceIndex

IMAGE_DIR = "vit/preprocess/datasets/face"
FACE_INDEX_PATH = "vit/preprocess/datasets/face_index.json"


def main():
    face_detector = FaceDetector()
    face_index = FaceIndex(FACE_INDEX_PATH)

    for name in sorted(os.listdir(IMAGE_DIR))[:20]:
        path = os.path.join(IMAGE_DIR, name)
        image = cv2.imread(path)

        if image is None:
            continue

        is_face = has_real_face(
            image=image,
            face_detector=face_detector,
            face_index=face_index,
            similarity_th=0.78,        # 최종값
            debug=True,
            apply_bbox_filter=False   # 핵심
        )

        print(f"{name} -> {'MODEL' if is_face else 'PRODUCT'}")


if __name__ == "__main__":
    main()
