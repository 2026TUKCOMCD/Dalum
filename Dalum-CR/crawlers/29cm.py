from playwright.sync_api import sync_playwright
import csv
import time
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# ===============================
# 출력 설정
# ===============================
OUTPUT_CSV = "29cm_products.csv"
MAX_PAGES_PER_CATEGORY = 300      # 안전장치(원하면 키워)
PAGE_PAUSE_SEC = 0.25
EMPTY_PAGES_STOP = 2              # 연속 N페이지 신규 0개면 종료


# ===============================
# ✅ URL만 채우면 되는 템플릿
# key: (대분류, 중분류, 하위분류)
# value: 29cm category list URL (page=1 포함)
# ===============================
CATEGORIES = {
    # ---------------- OUTER / 아우터 ----------------
    ("OUTER", "아우터", "야상"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102122&page=1",
    ("OUTER", "아우터", "블루종"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102123&page=1",
    ("OUTER", "아우터", "바시티"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102124&page=1",
    ("OUTER", "아우터", "데님 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102125&page=1",
    ("OUTER", "아우터", "퍼 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102126&page=1",
    ("OUTER", "아우터", "트레이닝 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102127&page=1",
    ("OUTER", "아우터", "점퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102128&page=1",
    ("OUTER", "아우터", "바람막이"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102129&page=1",
    ("OUTER", "아우터", "아노락"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102130&page=1",
    ("OUTER", "아우터", "후드 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102109&page=1",
    ("OUTER", "아우터", "플리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102114&page=1",
    ("OUTER", "아우터", "무스탕"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102116&page=1",
    ("OUTER", "아우터", "트렌치/맥코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102102&page=1",
    ("OUTER", "아우터", "나일론/코치 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102112&page=1",
    ("OUTER", "아우터", "베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102106&page=1",
    ("OUTER", "아우터", "레더 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102111&page=1",
    ("OUTER", "아우터", "블레이저"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102110&page=1",
    ("OUTER", "아우터", "숏코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102117&page=1",
    ("OUTER", "아우터", "하프코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102118&page=1",
    ("OUTER", "아우터", "롱코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102119&page=1",
    ("OUTER", "아우터", "경량패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102105&page=1",
    ("OUTER", "아우터", "숏패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102104&page=1",
    ("OUTER", "아우터", "롱패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102103&page=1",
    ("OUTER", "아우터", "기타 아우터"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102113&page=1",

    # ---------------- TOP / 상의 ----------------
    ("TOP", "상의", "반소매 셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "반소매 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "피케/카라 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=x",
    ("TOP", "상의", "슬리브리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "스웨트셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "후디"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "긴소매 셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "상의", "긴소매 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- TOP / 니트웨어 ----------------
    ("TOP", "니트웨어", "기타 니트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "크루넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "브이넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "터틀넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "폴로셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "니트 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "카디건"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "니트 베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "니트웨어", "니트 후드"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- BOTTOM / 하의 ----------------
    ("BOTTOM", "하의", "부츠컷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "레깅스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104110&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "쇼트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "슬림 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "스트레이트 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "와이드 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "데님 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "트레이닝 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "슬랙스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "코튼 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "하의", "기타 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104111&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- TOP/BOTTOM/DRESS / 홈웨어 ----------------
    ("TOP", "홈웨어", "홈웨어 상의"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "홈웨어", "홈웨어 하의"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "홈웨어", "홈웨어 세트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "홈웨어", "로브"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- DRESS / 셋업 ----------------
    ("DRESS", "셋업", "수트 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "셋업", "기타 상하의 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "셋업", "스웻/트레이닝 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- ACCESSORY / 이너웨어 ----------------
    ("ACCESSORY", "이너웨어", "팬티"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272105100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272105101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("ACCESSORY", "이너웨어", "언더셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272105100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272105102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("ACCESSORY", "이너웨어", "내의/내복"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272105100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272105104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("ACCESSORY", "이너웨어", "기타 언더웨어"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272105100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272105105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- BAG / 가방 ----------------
    ("BAG", "가방", "보스턴백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273119100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "캐리어/여행가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273118100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "크로스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273101100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "토트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273103100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "웨이스트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273102100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "백팩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273104100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "숄더백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273105100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "랩탑백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273106100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "에코/캔버스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273107100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "클러치"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273115100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "가방", "기타 가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273110100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # ---------------- SHOES / 신발 ----------------
    ("SHOES", "신발", "스니커즈"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274101100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "기능화"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274115100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "구두"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274103100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "부츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274104100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "로퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274102100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "샌들"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274105100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "신발", "슬리퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274110100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
}


# ===============================
# 유틸
# ===============================
def set_page(url: str, page_num: int) -> str:
    u = urlparse(url)
    q = parse_qs(u.query)
    q["page"] = [str(page_num)]
    return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, doseq=True), u.fragment))

def only_digits(s: str) -> str:
    return re.sub(r"[^\d]", "", s or "")

def calc_original_price(sell_price: str, discount_rate: str) -> str:
    sell = only_digits(sell_price)
    rate = only_digits(discount_rate)

    if not sell:
        return ""
    sell = int(sell)

    if not rate:
        return str(sell)

    rate = int(rate)
    if rate <= 0 or rate >= 100:
        return str(sell)

    return str(round(sell / (1 - rate / 100)))


# ===============================
# 목록 카드 추출 JS
# ===============================
JS_EXTRACT = r"""
() => {
  const results = [];
  const anchors = document.querySelectorAll("a[href^='https://product.29cm.co.kr/catalog/']");

  for (const a of anchors) {
    const href = a.href || "";
    if (!href.includes("product.29cm.co.kr/catalog/")) continue;

    const img = a.querySelector("img");
    const name = (img?.getAttribute("alt") || "").trim();

    let imgUrl = (img?.getAttribute("src") || "").trim();
    if (!imgUrl) {
      const srcset = (img?.getAttribute("srcset") || "").trim();
      if (srcset) imgUrl = srcset.split(",")[0].trim().split(" ")[0].trim();
    }

    const box = a.closest("li") || a.parentElement || a;

    let price = "", discount = "";
    let priceBox = box?.querySelector("div.items-center");
    if (!priceBox) priceBox = box?.querySelector("div[class*='items-center']");
    if (priceBox) {
      const ps = priceBox.querySelectorAll("p");
      if (ps.length >= 2) {
        discount = (ps[0].textContent || "").trim();
        price = (ps[1].textContent || "").trim();
      } else if (ps.length === 1) {
        price = (ps[0].textContent || "").trim();
      }
    }

    let brand = "";
    const lines = (box?.innerText || "").split("\n").map(v => v.trim()).filter(Boolean);
    if (name && lines.length) {
      const idx = lines.findIndex(v => v.includes(name));
      if (idx > 0) brand = lines[idx - 1];
    }
    if (brand && brand.length > 40) brand = "";

    results.push({ href, name, brand, price, discount, imgUrl });
  }
  return results;
}
"""


# ===============================
# 메인 크롤러
# ===============================
def scrape():
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "대분류",
                "중분류",
                "카테고리",
                "상품명",
                "브랜드",
                "정가",
                "판매가",
                "할인율(%)",
                "상품 URL",
                "이미지 URL",
            ],
        )
        writer.writeheader()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1400, "height": 900})

            def block(route, request):
                if request.resource_type in ["image", "media", "font"]:
                    return route.abort()
                return route.continue_()

            page = context.new_page()
            page.route("**/*", block)

            seen = set()

            for (main_cat, mid_cat, sub_cat), base_url in CATEGORIES.items():
                if not base_url.strip():
                    print(f"⏭ URL 없음 → 스킵: {main_cat}/{mid_cat}/{sub_cat}")
                    continue

                print(f"\n📂 START: {main_cat} / {mid_cat} / {sub_cat}")
                empty_pages = 0

                for page_num in range(1, MAX_PAGES_PER_CATEGORY + 1):
                    url = set_page(base_url, page_num)
                    print(f"  ▶ page={page_num}")

                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        page.wait_for_selector("a[href^='https://product.29cm.co.kr/catalog/']", timeout=30000)
                    except Exception:
                        break

                    time.sleep(PAGE_PAUSE_SEC)
                    items = page.evaluate(JS_EXTRACT)

                    added = 0
                    for it in items:
                        href = it.get("href", "")
                        if not href or href in seen:
                            continue
                        seen.add(href)
                        added += 1

                        sell = only_digits(it.get("price", ""))
                        rate = only_digits(it.get("discount", ""))
                        original = calc_original_price(sell, rate)

                        writer.writerow({
                            "대분류": main_cat,
                            "중분류": mid_cat,
                            "카테고리": sub_cat,
                            "상품명": it.get("name", "") or "",
                            "브랜드": it.get("brand", "") or "",
                            "정가": original,
                            "판매가": sell,
                            "할인율(%)": rate,
                            "상품 URL": href,
                            "이미지 URL": it.get("imgUrl", "") or "",
                        })

                    if added == 0:
                        empty_pages += 1
                        if empty_pages >= EMPTY_PAGES_STOP:
                            break
                    else:
                        empty_pages = 0

                print(f"✅ END: {main_cat}/{mid_cat}/{sub_cat}")

            browser.close()

    print(f"\n✅ CSV 생성 완료: {OUTPUT_CSV}")


if __name__ == "__main__":
    scrape()
