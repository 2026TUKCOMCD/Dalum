import cv2
import numpy as np


def hex_to_lab(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # OpenCV는 BGR 입력
    bgr = np.uint8([[rgb[::-1]]])
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0][0]

    return lab.tolist()


def normalize_lab(lab):
    L, A, B = lab

    L = L / 100.0
    A = (A + 128) / 255.0
    B = (B + 128) / 255.0

    return [L, A, B]


def build_color_embedding(dominant_colors):
    embedding = []

    for hex_color, ratio in dominant_colors:
        lab = hex_to_lab(hex_color)
        lab = normalize_lab(lab)

        # ratio 반영 (가중 평균 효과)
        weighted = [c * ratio for c in lab]

        embedding.extend(weighted)

    return embedding
