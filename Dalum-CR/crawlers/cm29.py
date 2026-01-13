from playwright.sync_api import sync_playwright
import csv
import time
import re
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "29cm")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_PAGES_PER_CATEGORY = 300
PAGE_PAUSE_SEC = 0.25
EMPTY_PAGES_STOP = 2


CATEGORIES = {
    # OUTER
    ("OUTER", "JACKET", "블루종"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102123&page=1",
    ("OUTER", "JACKET", "바시티"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102124&page=1",
    ("OUTER", "JACKET", "데님 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102125&page=1",
    ("OUTER", "JACKET", "퍼 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102126&page=1",
    ("OUTER", "JACKET", "무스탕"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102116&page=1",
    ("OUTER", "JACKET", "레더 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102111&page=1",
    
    ("OUTER", "JACKET", "점퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102128&page=1",
    ("OUTER", "JACKET", "바람막이"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102129&page=1",
    ("OUTER", "JACKET", "아노락"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102130&page=1",
    ("OUTER", "JACKET", "나일론/코치 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102112&page=1",
    ("OUTER", "JACKET", "블레이저"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102110&page=1",
    ("OUTER", "JACKET", "야상"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102122&page=1",
    ("OUTER", "JACKET", "트레이닝 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102127&page=1",


    ("OUTER", "HOODED_ZIP_UP", "후드 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102109&page=1",

    ("OUTER", "VEST", "베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102106&page=1",

    ("OUTER", "COAT", "트렌치/맥코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102102&page=1",
    ("OUTER", "COAT", "숏코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102117&page=1",
    ("OUTER", "COAT", "하프코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102118&page=1",
    ("OUTER", "COAT", "롱코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102119&page=1",

    ("OUTER", "PADDING", "경량패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102105&page=1",
    ("OUTER", "PADDING", "숏패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102104&page=1",
    ("OUTER", "PADDING", "롱패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102103&page=1",

    ("OUTER", "ETC_OUTER", "기타 아우터"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102113&page=1",


    # TOP
    ("TOP", "TSHIRT", "반소매 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "TSHIRT", "피케/카라 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=x",
    ("TOP", "TSHIRT", "슬리브리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "SWEATSHIRT", "스웨트셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "HOODIE", "후디"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "HOODIE", "집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "SHIRT_BLOUSE", "반소매셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "SHIRT_BLOUSE", "긴소매셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "LSHIRT", "긴소매티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    ("TOP", "FLEECE", "플리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102114&page=1",

    ("TOP", "KNIT", "기타니트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "크루넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "브이넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "터틀넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "폴로셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "니트 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "카디건"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "니트베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("TOP", "KNIT", "니트후드"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # BOTTOM
    ("BOTTOM", "COTTON_PANTS", "부츠컷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104109&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "LEGGINGS", "레깅스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104110&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "SHORTS", "쇼트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104108&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "COTTON_PANTS", "슬림팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "COTTON_PANTS", "스트레이트팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "COTTON_PANTS", "와이드팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104102&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "DENIM", "데님팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "TRAINING_PANTS", "트레이닝팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104107&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "SLACKS", "슬랙스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104106&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "COTTON_PANTS", "코튼팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104105&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BOTTOM", "ETC_BOTTOM", "기타팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104111&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",



    # DRESS
    ("DRESS", "SETUP", "수트셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112101&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "SETUP", "기타상하의셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112104&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("DRESS", "SETUP", "스웻/트레이닝셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112103&page=1&colors=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # BAG
    ("BAG", "ETC_BAG", "보스턴백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273119100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "ETC_BAG", "캐리어/여행가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273118100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "CROSSBODY", "크로스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273101100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "TOTE", "토트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273103100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "ETC_BAG", "웨이스트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273102100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "BACKPACK", "백팩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273104100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "SHOULDER", "숄더백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273105100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "ETC_BAG", "랩탑백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273106100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "TOTE", "에코/캔버스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273107100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "CLUTCH", "클러치"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273115100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("BAG", "ETC_BAG", "기타가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=273110100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    # SHOES
    ("SHOES", "SNEAKERS", "스니커즈"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274101100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "SPORTS_SHOES", "기능화"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274115100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "ETC_SHOES", "구두"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274103100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "BOOTS", "부츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274104100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "LOAFER", "로퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274102100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "SANDAL_SLIPPER", "샌들"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274105100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",
    ("SHOES", "SANDAL_SLIPPER", "슬리퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&colors=&categoryMediumCode=274110100&categorySmallCode=&minPrice=&maxPrice=&isFreeShipping=&excludeSoldOut=&isDiscount=&brands=&tag=&extraFacets=&attributes=&ticketEndDate=&ticketStartDate=",

    #HAT
    ("HAT", "CAP", "볼캡"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101103&page=1",
    ("HAT", "BEANIE", "비니"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101104&page=1",
    ("HAT", "BALACLAVA", "바라클라바"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101106&page=1",
    ("HAT", "TROOPER", "트루퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101107&page=1",
    ("HAT", "FEDORA", "페도라"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101105&page=1",
    ("HAT", "BERET", "베레모"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101102&page=1",
    ("HAT", "ETC_HAT", "기타모자"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=275101108&page=1"

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

  const pickPriceDiscount = (box) => {
    // box 안에 있는 모든 p 텍스트 수집
    const ps = Array.from(box.querySelectorAll("p"))
      .map(p => (p.textContent || "").trim())
      .filter(Boolean);

    // % 할인율 후보
    const percent = ps.find(t => /%/.test(t)) || "";

    // 가격 후보(숫자/콤마만 있는 형태 포함)
    const moneyCandidates = ps
      .filter(t => /[\d,]+/.test(t))
      .map(t => t.replace(/[^\d]/g, ""))        // 숫자만
      .filter(v => v.length >= 4);             // 1000원 이상만 대충 필터

    // 카드에 가격이 2개(정가/판매가)면 보통 큰 값이 정가, 작은 값이 판매가일 때가 많고
    // 1개면 판매가만 있는 경우가 많음
    let price = "";
    let discount = percent;

    if (moneyCandidates.length === 1) {
      price = moneyCandidates[0];
    } else if (moneyCandidates.length >= 2) {
      // 가장 자주 나오는 케이스: [할인율, 판매가] 또는 [정가, 판매가] 등 섞임
      // 일단 "가장 작은 값"을 판매가로 두는 게 안전한 편
      const nums = moneyCandidates.map(v => parseInt(v, 10)).filter(n => !isNaN(n));
      nums.sort((a,b)=>a-b);
      price = String(nums[0]); // 판매가 후보
    }

    return { price, discount };
  };

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

    // ✅ 여기서부터 핵심 변경: items-center 한 방이 아니라, box 전체에서 "가격/할인"을 스캔
    const { price, discount } = pickPriceDiscount(box);

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
    rows_by_major = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})

        page = context.new_page()
        seen = set()

        for (main_cat, mid_cat, sub_cat), base_url in CATEGORIES.items():
            print(f"\n📂 START: {main_cat} / {mid_cat} / {sub_cat}")
            empty_pages = 0

            for page_num in range(1, MAX_PAGES_PER_CATEGORY + 1):
                url = set_page(base_url, page_num)

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_selector(
                        "a[href^='https://product.29cm.co.kr/catalog/']",
                        timeout=30000
                    )
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

                    rows_by_major.setdefault(main_cat, []).append([
                        main_cat,
                        mid_cat,
                        sub_cat,
                        it.get("brand", "") or "",
                        it.get("name", "") or "",
                        original,
                        sell,
                        rate,
                        href,
                        it.get("imgUrl", "") or "",
                    ])

                if added == 0:
                    empty_pages += 1
                    if empty_pages >= EMPTY_PAGES_STOP:
                        break
                else:
                    empty_pages = 0

            print(f"✅ END: {main_cat}/{mid_cat}/{sub_cat}")

        browser.close()

    # ===============================
    # 대분류별 CSV 저장 (헤더 ❌)
    # ===============================
    for major, rows in rows_by_major.items():
        path = os.path.join(OUTPUT_DIR, f"{major}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"✅ 29cm/{major}.csv 저장 ({len(rows)}개)")

# ===============================
if __name__ == "__main__":
    scrape()