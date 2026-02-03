"""
Segformer 의류 세그멘테이션 - 최종 개선 버전
문제점 해결:
1. 양말 오인식 → 다리 레이블 제거
2. 바지 분리 실패 → 세그멘테이션 정확도 향상
3. 과도한 도려냄 → Convex Hull 비활성화, 파라미터 조정
4. 바지 중앙 구멍 → Closing 강화
5. 벨트 오인식 → 벨트/상의 레이블 명시적 제거
"""

import torch
import psycopg2
import requests
from PIL import Image, ImageDraw
from io import BytesIO
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
import numpy as np
import pandas as pd
from datetime import datetime
import os
import cv2
from collections import Counter
import base64
from rembg import remove

# ============================================================
# 🎯 테스트 설정
# ============================================================
# 테스트할 카테고리 선택 (원하는 카테고리 주석 해제)
TEST_CATEGORIES = ['OUTER']  # 현재 테스트 중
# TEST_CATEGORIES = ['TOP']
# TEST_CATEGORIES = ['OUTER']
# TEST_CATEGORIES = ['DRESS']
# TEST_CATEGORIES = ['SHOES']
# TEST_CATEGORIES = ['BAG']
# TEST_CATEGORIES = ['HAT']
# TEST_CATEGORIES = ['TOP', 'BOTTOM', 'OUTER']  # 여러 카테고리 동시 테스트
# TEST_CATEGORIES = ['TOP', 'BOTTOM', 'OUTER', 'DRESS', 'SHOES', 'BAG', 'HAT']  # 전체

SAMPLES_PER_CATEGORY = 50  # 카테고리당 샘플 수
SAMPLES_PER_MALL = 10      # 쇼핑몰당 샘플 수
# ============================================================

# DB 설정
DB_CONFIG = {
    'host': 'localhost',
    'port': 8080,
    'database': 'postgres',
    'user': 'postgres',
    'password': '6532aa'
}

# ============================================================
# 🔧 최종 개선된 카테고리별 세그멘테이션 파라미터
# ============================================================
SEGMENTATION_PARAMS = {
    'TOP': {
        'morph_kernel_size': 5,
        'min_area_ratio': 0.02,
        'use_largest_only': True,
        'closing_iterations': 10,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 3
    },
    'OUTER': {
        'morph_kernel_size': 5,
        'min_area_ratio': 0.02,
        'use_largest_only': True,
        'closing_iterations': 10,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 3
    },
    'BOTTOM': {
        'morph_kernel_size': 7,        # 3 → 5 (구멍 메우기 강화)
        'min_area_ratio': 0.005,
        'use_largest_only': True,
        'closing_iterations': 15,      # 8 → 15 (구멍 메우기 핵심!)
        'opening_iterations': 1,
        'use_convex_hull': False,
        'dilate_final': 3              # 2 → 3 (최종 확장)
    },
    # 추가 카테고리 (기본값 사용, 필요시 조정)
    'DRESS': {
        'morph_kernel_size': 5,
        'min_area_ratio': 0.02,
        'use_largest_only': True,
        'closing_iterations': 10,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 3
    },
    'SHOES': {
        'morph_kernel_size': 3,
        'min_area_ratio': 0.01,
        'use_largest_only': False,  # 양쪽 신발 모두 포함
        'closing_iterations': 8,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 2
    },
    'BAG': {
        'morph_kernel_size': 5,
        'min_area_ratio': 0.015,
        'use_largest_only': True,
        'closing_iterations': 10,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 3
    },
    'HAT': {
        'morph_kernel_size': 3,
        'min_area_ratio': 0.008,
        'use_largest_only': True,
        'closing_iterations': 8,
        'opening_iterations': 2,
        'use_convex_hull': False,
        'dilate_final': 2
    }
}

print("모델 로딩 중...")
print("  - ViT 모델 로딩...")
from transformers import ViTImageProcessor, ViTModel
vit_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224-in21k')
vit_model = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
vit_model.eval()

print("  - Segformer 의류 세그멘테이션 모델 로딩...")
seg_processor = AutoImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
seg_model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
seg_model.eval()

print("모델 로딩 완료!\n")

# 의류 레이블 매핑
LABEL_NAMES = [
    'Background', 'Hat', 'Hair', 'Sunglasses', 'Upper-clothes', 
    'Skirt', 'Pants', 'Dress', 'Belt', 'Left-shoe', 
    'Right-shoe', 'Face', 'Left-leg', 'Right-leg', 'Left-arm', 
    'Right-arm', 'Bag', 'Scarf'
]

# ============================================================
# 🔧 개선: 카테고리별 관심 레이블
# ============================================================
CATEGORY_LABELS = {
    'TOP': ['Upper-clothes'],
    'BOTTOM': ['Pants', 'Skirt'],  # 다리 레이블 제거로 양말 오인식 방지
    'OUTER': ['Upper-clothes'],
    'DRESS': ['Dress'],
    'SHOES': ['Left-shoe', 'Right-shoe'],
    'BAG': ['Bag'],
    'HAT': ['Hat']
}

# 참고: Segformer 모델의 전체 레이블 목록
# 'Background', 'Hat', 'Hair', 'Sunglasses', 'Upper-clothes', 
# 'Skirt', 'Pants', 'Dress', 'Belt', 'Left-shoe', 
# 'Right-shoe', 'Face', 'Left-leg', 'Right-leg', 'Left-arm', 
# 'Right-arm', 'Bag', 'Scarf'

def download_image(url, timeout=10):
    """이미지 다운로드"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert('RGB')
        return image
    except Exception as e:
        return None

def segment_clothing(image, category):
    """
    최종 개선된 세그멘테이션
    - 벨트/상의 오염 제거
    - 구멍 메우기 강화
    """
    try:
        params = SEGMENTATION_PARAMS.get(category, SEGMENTATION_PARAMS['TOP'])
        morph_kernel_size = params['morph_kernel_size']
        min_area_ratio = params['min_area_ratio']
        use_largest_only = params['use_largest_only']
        closing_iterations = params['closing_iterations']
        opening_iterations = params['opening_iterations']
        use_convex_hull = params.get('use_convex_hull', False)
        dilate_final = params.get('dilate_final', 0)
        
        # 이미지 전처리
        inputs = seg_processor(images=image, return_tensors="pt")
        
        # 세그멘테이션 실행
        with torch.no_grad():
            outputs = seg_model(**inputs)
        
        logits = outputs.logits
        upsampled_logits = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1],
            mode='bilinear',
            align_corners=False
        )
        
        pred_seg = upsampled_logits.argmax(dim=1)[0].cpu().numpy()
        
        # 카테고리별 관심 레이블 추출
        target_labels = CATEGORY_LABELS.get(category, ['Upper-clothes'])
        
        # 마스크 생성
        mask = np.zeros_like(pred_seg, dtype=np.uint8)
        for label_name in target_labels:
            if label_name in LABEL_NAMES:
                label_idx = LABEL_NAMES.index(label_name)
                mask[pred_seg == label_idx] = 255
        
        # ========== 🔧 카테고리별 오염 제거 ==========
        if category == 'BOTTOM':
            # 벨트 제거 (바지에 벨트가 포함되는 문제)
            if 'Belt' in LABEL_NAMES:
                belt_idx = LABEL_NAMES.index('Belt')
                mask[pred_seg == belt_idx] = 0
                print(f"  🔧 벨트 영역 제거")
            
            # 상의도 혹시 포함되었으면 제거
            if 'Upper-clothes' in LABEL_NAMES:
                upper_idx = LABEL_NAMES.index('Upper-clothes')
                mask[pred_seg == upper_idx] = 0
        
        elif category == 'TOP':
            # 상의에서 바지/치마 제거
            for label_name in ['Pants', 'Skirt']:
                if label_name in LABEL_NAMES:
                    idx = LABEL_NAMES.index(label_name)
                    mask[pred_seg == idx] = 0
        # ==========================================
        
        # 초기 마스크 검증
        total_pixels = mask.shape[0] * mask.shape[1]
        mask_pixels = np.sum(mask > 0)
        mask_ratio = mask_pixels / total_pixels
        
        if mask_ratio < 0.005:
            print(f"  ⚠️ 마스크 영역이 너무 작음 ({mask_ratio*100:.2f}%)")
            return None, None
        
        # ========== 후처리 ==========
        
        # 1. Opening (노이즈 제거)
        if opening_iterations > 0:
            kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, 
                                    iterations=opening_iterations)
        
        # 2. Closing (구멍 메우기) - 강화됨!
        if closing_iterations > 0:
            kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, 
                                    iterations=closing_iterations)
            print(f"  🔧 Closing {closing_iterations}회 적용 (구멍 메우기)")
        
        # 3. 연결 컴포넌트 분석
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8)
        
        if num_labels <= 1:
            print(f"  ⚠️ 유효한 영역 없음")
            return None, None
        
        # 4. 영역 필터링
        min_area = total_pixels * min_area_ratio
        filtered_mask = np.zeros_like(mask)
        
        if use_largest_only:
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            filtered_mask[labels == largest_label] = 255
            print(f"  ✅ 가장 큰 영역 선택")
        else:
            valid_count = 0
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area >= min_area:
                    filtered_mask[labels == i] = 255
                    valid_count += 1
            
            if valid_count > 15:
                print(f"  ⚠️ 영역이 너무 파편화됨 ({valid_count}개)")
                return None, None
            
            print(f"  ✅ {valid_count}개 영역 선택")
        
        # 5. BOTTOM 전용: 바운딩 박스 확장 + 상단 자르기
        if category == 'BOTTOM':
            coords = np.column_stack(np.where(filtered_mask > 0))
            if len(coords) > 0:
                y_min, x_min = coords.min(axis=0)
                y_max, x_max = coords.max(axis=0)
                
                height = y_max - y_min
                width = x_max - x_min
                
                # 🔧 상단 자르기 (벨트 영역 추가 제거)
                y_cut = int(y_min + height * 0.05)  # 상단 5% 제거
                filtered_mask[:y_cut, :] = 0
                print(f"  🔧 상단 5% 제거 (벨트 방지)")
                
                # 확장 비율
                y_extend = int(height * 0.15)
                x_extend = int(width * 0.1)
                
                y_min_new = max(y_cut, y_min - y_extend)  # y_cut 이상으로만
                y_max_new = min(mask.shape[0], y_max + y_extend)
                x_min_new = max(0, x_min - x_extend)
                x_max_new = min(mask.shape[1], x_max + x_extend)
                
                extended_mask = np.zeros_like(filtered_mask)
                
                # Pants, Skirt만 사용
                for label_name in ['Pants', 'Skirt']:
                    if label_name in LABEL_NAMES:
                        label_idx = LABEL_NAMES.index(label_name)
                        label_mask = (pred_seg == label_idx).astype(np.uint8) * 255
                        label_mask[:y_min_new, :] = 0
                        label_mask[y_max_new:, :] = 0
                        label_mask[:, :x_min_new] = 0
                        label_mask[:, x_max_new:] = 0
                        extended_mask = cv2.bitwise_or(extended_mask, label_mask)
                
                if np.sum(extended_mask > 0) > np.sum(filtered_mask > 0):
                    filtered_mask = extended_mask
                    print(f"  ✅ 바운딩 박스 확장 적용")
                    
                    # 추가 구멍 메우기
                    kernel = np.ones((7, 7), np.uint8)
                    filtered_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, 
                                                    kernel, iterations=5)
        
        # 6. Convex Hull (비활성화)
        # use_convex_hull = False
        
        # 7. 최종 확장
        if dilate_final > 0:
            kernel = np.ones((dilate_final, dilate_final), np.uint8)
            filtered_mask = cv2.dilate(filtered_mask, kernel, iterations=1)
            filtered_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, 
                                            kernel, iterations=2)
            print(f"  ✅ 최종 확장 {dilate_final}px 적용")
        
        # 8. 최종 검증
        final_mask_pixels = np.sum(filtered_mask > 0)
        final_mask_ratio = final_mask_pixels / total_pixels
        
        if final_mask_ratio < 0.003:
            print(f"  ⚠️ 최종 마스크가 너무 작음 ({final_mask_ratio*100:.2f}%)")
            return None, None
        
        # 9. 평활화
        filtered_mask = cv2.GaussianBlur(filtered_mask, (5, 5), 0)
        _, filtered_mask = cv2.threshold(filtered_mask, 127, 255, cv2.THRESH_BINARY)
        
        mask_image = Image.fromarray(filtered_mask)
        
        print(f"  ✅ 최종 마스크 비율: {final_mask_ratio*100:.2f}%")
        
        return mask_image, pred_seg
        
    except Exception as e:
        print(f"  ⚠️ 세그멘테이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def apply_mask_and_crop(image, mask):
    """마스크 적용 및 크롭"""
    try:
        if mask is None:
            return image
        
        img_array = np.array(image)
        mask_array = np.array(mask)
        
        result = img_array.copy()
        result[mask_array == 0] = [255, 255, 255]
        
        masked_image = Image.fromarray(result)
        
        coords = np.column_stack(np.where(mask_array > 0))
        if len(coords) == 0:
            return masked_image
        
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(image.width, x_max + padding)
        y_max = min(image.height, y_max + padding)
        
        cropped = masked_image.crop((x_min, y_min, x_max, y_max))
        
        return cropped
        
    except Exception as e:
        print(f"  ⚠️ 마스크 적용 실패: {e}")
        return image

def remove_background_final(image):
    """최종 배경 제거"""
    try:
        output = remove(image)
        
        if output.mode == 'RGBA':
            background = Image.new('RGB', output.size, (255, 255, 255))
            background.paste(output, mask=output.split()[3])
            return background
        return output
    except Exception as e:
        print(f"  ⚠️ 배경 제거 실패: {e}")
        return image

def extract_dominant_colors(image, n_colors=5):
    """주요 색상 추출"""
    try:
        img_array = np.array(image)
        
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        mask = ~((hsv[:,:,2] > 240) & (hsv[:,:,1] < 30))
        
        img_small = cv2.resize(img_array, (100, 100))
        mask_small = cv2.resize(mask.astype(np.uint8), (100, 100))
        pixels = img_small[mask_small > 0].astype(np.float32)
        
        if len(pixels) < 100:
            pixels = img_small.reshape(-1, 3).astype(np.float32)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = min(n_colors, max(1, len(pixels)//10))
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        label_counts = Counter(labels.flatten())
        total_pixels = len(labels)
        
        color_info = []
        for i in range(len(centers)):
            color = centers[i].astype(int)
            ratio = label_counts[i] / total_pixels
            color_info.append({
                'rgb': tuple(color),
                'ratio': ratio,
                'hex': '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            })
        
        color_info.sort(key=lambda x: x['ratio'], reverse=True)
        return color_info
    except Exception as e:
        print(f"  ⚠️ 색상 추출 실패: {e}")
        return []

def visualize_segmentation(image, seg_map):
    """세그멘테이션 결과 시각화"""
    try:
        colors = [
            [0, 0, 0], [128, 0, 0], [255, 255, 0], [0, 85, 85],
            [0, 128, 0], [85, 0, 85], [0, 0, 255], [255, 0, 255],
            [85, 85, 0], [128, 128, 0], [128, 128, 0], [255, 192, 203],
            [0, 128, 128], [0, 128, 128], [128, 0, 128], [128, 0, 128],
            [64, 64, 64], [192, 192, 192]
        ]
        
        h, w = seg_map.shape
        seg_viz = np.zeros((h, w, 3), dtype=np.uint8)
        
        for label_idx, color in enumerate(colors):
            seg_viz[seg_map == label_idx] = color
        
        img_array = np.array(image.resize((w, h)))
        blended = cv2.addWeighted(img_array, 0.5, seg_viz, 0.5, 0)
        
        return Image.fromarray(blended)
        
    except Exception as e:
        print(f"  ⚠️ 시각화 실패: {e}")
        return image

def image_to_base64(image):
    """이미지를 base64로 변환"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def fetch_products_by_category(category, limit_per_mall=10):
    """카테고리별로 쇼핑몰당 N개씩 상품 가져오기"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        malls = ['musinsa', '29cm']
        all_products = []
        
        for mall in malls:
            query = """
                SELECT id, shopping_mall, brand, product_name, 
                       sale_price, image_url, main_category
                FROM all_product
                WHERE main_category = %s
                  AND shopping_mall = %s
                  AND image_url IS NOT NULL 
                  AND image_url != ''
                  AND image_url != '-'
                ORDER BY RANDOM()
                LIMIT %s
            """
            
            cursor.execute(query, (category, mall, limit_per_mall))
            rows = cursor.fetchall()
            all_products.extend(rows)
        
        cursor.close()
        conn.close()
        
        return all_products
    except Exception as e:
        print(f"❌ DB 연결 오류: {e}")
        return []

def generate_comparison_html(results, output_file='ai_segmentation_final.html'):
    """최종 개선 HTML 리포트 생성"""
    
    html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 의류 세그멘테이션 - 최종 버전</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1800px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 16px;
        }
        .improvements {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .improvements h3 {
            margin-top: 0;
        }
        .improvements ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .info-box {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .info-box h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .legend {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 30px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .category-section {
            margin-bottom: 40px;
        }
        .category-header {
            background: white;
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .category-header h2 {
            margin: 0;
            color: #2c3e50;
            display: inline-block;
        }
        .category-count {
            float: right;
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(650px, 1fr));
            gap: 20px;
        }
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .product-title {
            font-size: 15px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
            height: 38px;
            overflow: hidden;
        }
        .product-meta {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
        }
        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        .image-box {
            text-align: center;
        }
        .image-label {
            font-size: 11px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 8px;
            padding: 5px;
            background: #ecf0f1;
            border-radius: 5px;
            min-height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .image-box img {
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #f8f9fa;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }
        .color-comparison {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #ecf0f1;
        }
        .color-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
        }
        .color-section {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
        }
        .color-label {
            font-size: 11px;
            font-weight: bold;
            color: #7f8c8d;
            margin-bottom: 8px;
        }
        .color-palette {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }
        .color-swatch {
            width: 32px;
            height: 32px;
            border-radius: 5px;
            border: 2px solid #ddd;
            position: relative;
        }
        .color-swatch::after {
            content: attr(data-ratio);
            position: absolute;
            bottom: -18px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 9px;
            color: #7f8c8d;
            white-space: nowrap;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 5px;
        }
        .badge-success {
            background: #2ecc71;
            color: white;
        }
        .badge-warning {
            background: #f39c12;
            color: white;
        }
        .badge-info {
            background: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI 의류 세그멘테이션 - 최종 버전</h1>
        <p class="subtitle">
            Segformer로 상의/하의 자동 분리 - 모든 문제 해결!
        </p>
        
        <div class="improvements">
            <h3>✨ 최종 개선 사항</h3>
            <ul>
                <li><strong>양말 오인식 해결:</strong> BOTTOM 레이블에서 다리 제거</li>
                <li><strong>과도한 도려냄 방지:</strong> Convex Hull 비활성화</li>
                <li><strong>바지 중앙 구멍 해결:</strong> Closing 15회로 강화 (8→15)</li>
                <li><strong>벨트 오인식 해결:</strong> 벨트/상의 레이블 명시적 제거</li>
                <li><strong>상단 오염 제거:</strong> 바지 상단 5% 자르기 적용</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h3>📚 세그멘테이션 레이블 안내</h3>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #0000ff;"></div>
                    <span>바지 (Pants) ✅</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #550055;"></div>
                    <span>치마 (Skirt) ✅</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #555500;"></div>
                    <span>벨트 (Belt) ❌ 제거됨</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #008080;"></div>
                    <span>다리 (Legs) ❌ 제거됨</span>
                </div>
            </div>
        </div>
"""
    
    total = len(results)
    seg_success = sum(1 for r in results if r.get('seg_success', False))
    
    html += f"""
        <div class="info-box">
            <h3>📊 처리 결과</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: bold;">{total}</div>
                    <div style="font-size: 12px;">총 상품</div>
                </div>
                <div style="text-align: center; background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 15px; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: bold;">{seg_success}</div>
                    <div style="font-size: 12px;">세그멘테이션 성공</div>
                </div>
                <div style="text-align: center; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 15px; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: bold;">{total - seg_success}</div>
                    <div style="font-size: 12px;">세그멘테이션 실패</div>
                </div>
            </div>
        </div>
"""
    
    grouped = {}
    for r in results:
        cat = r['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(r)
    
    for category, items in grouped.items():
        html += f"""
        <div class="category-section">
            <div class="category-header">
                <h2>📦 {category}</h2>
                <span class="category-count">{len(items)}개 상품</span>
            </div>
            <div class="product-grid">
"""
        
        for item in items:
            product = item['product']
            seg_success = item.get('seg_success', False)
            
            original_colors = item.get('original_colors', [])
            ai_colors = item.get('ai_segmented_colors', [])
            
            def count_bright_colors(colors):
                return sum(1 for c in colors[:3] if all(v > 200 for v in c['rgb']))
            
            original_bright = count_bright_colors(original_colors)
            ai_bright = count_bright_colors(ai_colors)
            
            if seg_success and ai_bright < original_bright:
                status = "세그멘테이션 성공"
                status_class = "badge-success"
            elif seg_success:
                status = "세그멘테이션 적용"
                status_class = "badge-info"
            else:
                status = "세그멘테이션 실패"
                status_class = "badge-warning"
            
            html += f"""
                <div class="product-card">
                    <div class="product-title">{product['product_name']}</div>
                    <div class="product-meta">
                        <span>{product['brand']}</span>
                        <span>{product['shopping_mall']}</span>
                        <span>₩{product['sale_price']:,}</span>
                    </div>
                    
                    <div class="comparison-container">
                        <div class="image-box">
                            <div class="image-label">원본 이미지</div>
                            <img src="{item.get('original_image_base64', '')}" alt="원본">
                        </div>
                        <div class="image-box">
                            <div class="image-label">Segformer 인식 결과<br>(디버깅용)</div>
                            <img src="{item.get('seg_viz_base64', '')}" alt="세그멘테이션">
                        </div>
                        <div class="image-box">
                            <div class="image-label">{category} 최종 추출<br><span class="{status_class} badge">{status}</span></div>
                            <img src="{item.get('ai_segmented_base64', '')}" alt="최종 결과">
                        </div>
                    </div>
                    
                    <div class="color-comparison">
                        <div class="color-grid">
                            <div class="color-section">
                                <div class="color-label">원본 색상</div>
                                <div class="color-palette">
"""
            
            for color in original_colors[:5]:
                html += f"""<div class="color-swatch" style="background-color: {color['hex']};" data-ratio="{color['ratio']*100:.0f}%"></div>"""
            
            html += """
                                </div>
                            </div>
                            <div class="color-section">
                                <div class="color-label">기존 배경제거 색상</div>
                                <div class="color-palette">
"""
            
            for color in item.get('old_bg_removed_colors', [])[:5]:
                html += f"""<div class="color-swatch" style="background-color: {color['hex']};" data-ratio="{color['ratio']*100:.0f}%"></div>"""
            
            html += """
                                </div>
                            </div>
                            <div class="color-section">
                                <div class="color-label">AI 세그멘테이션 색상</div>
                                <div class="color-palette">
"""
            
            for color in ai_colors[:5]:
                html += f"""<div class="color-swatch" style="background-color: {color['hex']};" data-ratio="{color['ratio']*100:.0f}%"></div>"""
            
            html += """
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ HTML 리포트 생성: {output_file}")
    return output_file

def main():
    print("="*70)
    print("AI 의류 세그멘테이션 - 최종 버전")
    print("="*70)
    print(f"\n테스트 카테고리: {', '.join(TEST_CATEGORIES)}")
    print(f"카테고리당 샘플: {SAMPLES_PER_CATEGORY}개")
    print(f"쇼핑몰당 샘플: {SAMPLES_PER_MALL}개\n")
    
    all_results = []
    
    for category in TEST_CATEGORIES:
        print(f"\n{'='*70}")
        print(f"📦 {category} 카테고리 처리 중...")
        print(f"{'='*70}")
        
        # 파라미터 출력
        params = SEGMENTATION_PARAMS[category]
        print(f"\n🎛️ {category} 최종 파라미터:")
        for key, value in params.items():
            print(f"  - {key}: {value}")
        print()
        
        products = fetch_products_by_category(category, SAMPLES_PER_MALL)
        
        if not products:
            print(f"⚠️ {category} 카테고리 상품을 찾을 수 없습니다.")
            continue
        
        print(f"✅ {len(products)}개 상품 로드 완료\n")
        
        for idx, product_data in enumerate(products, 1):
            product_id = product_data[0]
            shopping_mall = product_data[1]
            brand = product_data[2]
            product_name = product_data[3] if product_data[3] is not None else "상품명 없음"
            sale_price = product_data[4]
            image_url = product_data[5]
            main_category = product_data[6]
            
            print(f"[{idx}/{len(products)}] {product_name[:40]}...")
            print(f"  쇼핑몰: {shopping_mall}")
            
            # 원본 이미지
            print(f"  📸 이미지 다운로드...")
            original_image = download_image(image_url)
            if original_image is None:
                print(f"  ❌ 다운로드 실패\n")
                continue
            print(f"  ✅ 완료 ({original_image.width}x{original_image.height})")
            
            # 원본 색상
            print(f"  🎨 원본 색상 분석...")
            original_colors = extract_dominant_colors(original_image)
            
            # 기존 방식
            print(f"  ⚙️ 기존 방식 (배경 제거만)...")
            old_bg_removed = remove_background_final(original_image)
            old_bg_removed_colors = extract_dominant_colors(old_bg_removed)
            
            # AI 세그멘테이션
            print(f"  🤖 AI 세그멘테이션 실행...")
            mask, seg_map = segment_clothing(original_image, category)
            
            seg_success = mask is not None
            
            if seg_success:
                print(f"  ✅ 세그멘테이션 성공")
                
                seg_viz = visualize_segmentation(original_image, seg_map)
                
                print(f"  ✂️ {category} 영역 추출...")
                ai_segmented = apply_mask_and_crop(original_image, mask)
                print(f"  ✅ 추출 완료 ({ai_segmented.width}x{ai_segmented.height})")
                
                print(f"  🎨 AI 세그멘테이션 색상 분석...")
                ai_colors = extract_dominant_colors(ai_segmented)
                
                if original_colors and ai_colors:
                    print(f"  📊 색상 비교:")
                    print(f"     원본: {original_colors[0]['hex']} ({original_colors[0]['ratio']*100:.1f}%)")
                    print(f"     기존: {old_bg_removed_colors[0]['hex'] if old_bg_removed_colors else 'N/A'}")
                    print(f"     AI: {ai_colors[0]['hex']} ({ai_colors[0]['ratio']*100:.1f}%)")
            else:
                print(f"  ⚠️ 세그멘테이션 실패 - 기존 방식 사용")
                seg_viz = original_image
                ai_segmented = old_bg_removed
                ai_colors = old_bg_removed_colors
            
            print()
            
            all_results.append({
                'category': category,
                'product': {
                    'id': product_id,
                    'product_name': product_name,
                    'brand': brand,
                    'shopping_mall': shopping_mall,
                    'sale_price': int(sale_price) if sale_price not in ['-', ''] else 0,
                },
                'original_image_base64': image_to_base64(original_image),
                'seg_viz_base64': image_to_base64(seg_viz),
                'ai_segmented_base64': image_to_base64(ai_segmented),
                'original_colors': original_colors,
                'old_bg_removed_colors': old_bg_removed_colors,
                'ai_segmented_colors': ai_colors,
                'seg_success': seg_success
            })
    
    # HTML 리포트
    if all_results:
        print(f"\n{'='*70}")
        print("📊 결과 리포트 생성 중...")
        print(f"{'='*70}")
        
        html_file = generate_comparison_html(all_results)
        
        success = sum(1 for r in all_results if r['seg_success'])
        fail = len(all_results) - success
        
        print(f"\n{'='*70}")
        print("✅ 테스트 완료!")
        print(f"{'='*70}")
        print(f"\n총 {len(all_results)}개 상품 분석")
        print(f"  - AI 세그멘테이션 성공: {success}개")
        print(f"  - 세그멘테이션 실패: {fail}개")
        print(f"\nHTML 리포트: {html_file}")
    else:
        print("\n⚠️ 처리된 상품이 없습니다.")

if __name__ == "__main__":
    main()