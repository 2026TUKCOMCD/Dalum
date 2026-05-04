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

    # OpenCV uint8 LAB: L in [0,255], A in [0,255] (a+128), B in [0,255] (b+128)
    L = L / 255.0
    A = A / 255.0
    B = B / 255.0

    return [L, A, B]


def build_color_embedding(dominant_colors):
    embedding = []

    for hex_color, ratio in dominant_colors:
        lab = hex_to_lab(hex_color)
        lab = normalize_lab(lab)
        embedding.extend(lab)

    return embedding
