from playwright.sync_api import sync_playwright
import csv
import time
import re
import os
import random
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

# ===============================
# 설정
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "kream")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "https://kream.co.kr"
TARGET_PER_CATEGORY = 10

# ===============================
# 수집할 카테고리 URL (KREAM shop_category_id 기준)
# ===============================
CATEGORIES = {
    # OUTER
    "바람막이": "https://kream.co.kr/search?tab=49&shop_category_id=22&title=%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4&exclude_filter=shop_category_id",
    "경량패딩": "https://kream.co.kr/search?tab=49&shop_category_id=150&title=%EA%B2%BD%EB%9F%89+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "플리스자켓": "https://kream.co.kr/search?tab=49&shop_category_id=162&title=%ED%94%8C%EB%A6%AC%EC%8A%A4+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "숏패딩": "https://kream.co.kr/search?tab=49&shop_category_id=20&title=%EC%88%8F+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "트레이닝자켓": "https://kream.co.kr/search?tab=49&shop_category_id=165&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "후드자켓": "https://kream.co.kr/search?tab=49&shop_category_id=161&title=%ED%9B%84%EB%93%9C+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "블루종": "https://kream.co.kr/search?tab=49&shop_category_id=154&title=%EB%B8%94%EB%A3%A8%EC%A2%85&exclude_filter=shop_category_id",
    "아노락": "https://kream.co.kr/search?tab=49&shop_category_id=72&title=%EC%95%84%EB%85%B8%EB%9D%BD&exclude_filter=shop_category_id",
    "바시티자켓": "https://kream.co.kr/search?tab=49&shop_category_id=169&title=%EB%B0%94%EC%8B%9C%ED%8B%B0+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "블레이저": "https://kream.co.kr/search?tab=49&shop_category_id=156&title=%EB%B8%94%EB%A0%88%EC%9D%B4%EC%A0%80&exclude_filter=shop_category_id",
    "데님자켓": "https://kream.co.kr/search?tab=49&shop_category_id=166&title=%EB%8D%B0%EB%8B%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "워크자켓": "https://kream.co.kr/search?tab=49&shop_category_id=158&title=%EC%9B%8C%ED%81%AC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "레더자켓": "https://kream.co.kr/search?tab=49&shop_category_id=164&title=%EB%A0%88%EB%8D%94+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "코치자켓": "https://kream.co.kr/search?tab=49&shop_category_id=168&title=%EC%BD%94%EC%B9%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "퍼자켓": "https://kream.co.kr/search?tab=49&shop_category_id=160&title=%ED%8D%BC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "베스트": "https://kream.co.kr/search?tab=49&shop_category_id=153&title=%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "오버셔츠": "https://kream.co.kr/search?tab=49&shop_category_id=167&title=%EC%98%A4%EB%B2%84%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "기타자켓": "https://kream.co.kr/search?tab=49&shop_category_id=159&title=%EA%B8%B0%ED%83%80+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "롱코트": "https://kream.co.kr/search?tab=49&shop_category_id=21&title=%EB%A1%B1+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id&tmp=1768198817007",
    "숏코트": "https://kream.co.kr/search?tab=49&shop_category_id=163&title=%EC%88%8F+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "롱패딩": "https://kream.co.kr/search?tab=49&shop_category_id=149&title=%EB%A1%B1+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "퀼팅자켓": "https://kream.co.kr/search?tab=49&shop_category_id=157&title=%ED%80%BC%ED%8C%85+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "패딩베스트": "https://kream.co.kr/search?tab=49&shop_category_id=152&title=%ED%8C%A8%EB%94%A9+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "트렌치코트": "https://kream.co.kr/search?tab=49&shop_category_id=151&title=%ED%8A%B8%EB%A0%8C%EC%B9%98+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "기타아우터": "https://kream.co.kr/search?tab=49&shop_category_id=73&title=%EA%B8%B0%ED%83%80+%EC%95%84%EC%9A%B0%ED%84%B0&exclude_filter=shop_category_id",

    # TOP
    "후드": "https://kream.co.kr/search?tab=50&shop_category_id=23&title=%ED%9B%84%EB%93%9C&exclude_filter=shop_category_id",
    "긴소매 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=26&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "후드 집업": "https://kream.co.kr/search?tab=50&shop_category_id=74&title=%ED%9B%84%EB%93%9C+%EC%A7%91%EC%97%85&exclude_filter=shop_category_id",
    "스웨트셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=24&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=27&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 카라 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=188&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%EC%B9%B4%EB%9D%BC+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "긴소매 카라 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=189&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%EC%B9%B4%EB%9D%BC+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=191&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "긴소매 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=190&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "가디건": "https://kream.co.kr/search?tab=50&shop_category_id=75&title=%EA%B0%80%EB%94%94%EA%B1%B4&exclude_filter=shop_category_id",
    "크루넥니트": "https://kream.co.kr/search?tab=50&shop_category_id=195&title=%ED%81%AC%EB%A3%A8%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "브이넥니트": "https://kream.co.kr/search?tab=50&shop_category_id=193&title=%EB%B8%8C%EC%9D%B4%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "터틀넥니트": "https://kream.co.kr/search?tab=50&shop_category_id=194&title=%ED%84%B0%ED%8B%80%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "니트베스트": "https://kream.co.kr/search?tab=50&shop_category_id=196&title=%EB%8B%88%ED%8A%B8+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "블라우스": "https://kream.co.kr/search?tab=50&shop_category_id=192&title=%EB%B8%94%EB%9D%BC%EC%9A%B0%EC%8A%A4&exclude_filter=shop_category_id",
    "슬리브리스": "https://kream.co.kr/search?tab=50&shop_category_id=76&title=%EC%8A%AC%EB%A6%AC%EB%B8%8C%EB%A6%AC%EC%8A%A4&exclude_filter=shop_category_id",
    "수영복": "https://kream.co.kr/search?tab=50&shop_category_id=200&title=%EC%88%98%EC%98%81%EB%B3%B5&exclude_filter=shop_category_id",
    "기타상의": "https://kream.co.kr/search?tab=50&shop_category_id=78&title=%EA%B8%B0%ED%83%80+%EC%83%81%EC%9D%98&exclude_filter=shop_category_id",

    # BOTTOM
    "숏팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=175&title=%EC%88%8F+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "스웨트팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=176&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "트레이닝팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=177&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "데님팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=173&title=%EB%8D%B0%EB%8B%98+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "카고팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=174&title=%EC%B9%B4%EA%B3%A0+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "코튼팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=178&title=%EC%BD%94%ED%8A%BC+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "슬랙스": "https://kream.co.kr/search?tab=51&shop_category_id=179&title=%EC%8A%AC%EB%9E%99%EC%8A%A4&exclude_filter=shop_category_id",
    "레깅스": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "데님스커트": "https://kream.co.kr/search?tab=51&shop_category_id=184&title=%EB%8D%B0%EB%8B%98+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "미니스커트": "https://kream.co.kr/search?tab=51&shop_category_id=180&title=%EB%AF%B8%EB%8B%88+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "미디스커트": "https://kream.co.kr/search?tab=51&shop_category_id=181&title=%EB%AF%B8%EB%94%94+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "롱스커트": "https://kream.co.kr/search?tab=51&shop_category_id=182&title=%EB%A1%B1+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "오버올": "https://kream.co.kr/search?tab=51&shop_category_id=183&title=%EC%98%A4%EB%B2%84%EC%98%AC&exclude_filter=shop_category_id",
    "기타하의": "https://kream.co.kr/search?tab=51&shop_category_id=80&title=%EA%B8%B0%ED%83%80+%ED%95%98%EC%9D%98&exclude_filter=shop_category_id",

    # SHOES
    "스니커즈": "https://kream.co.kr/search?tab=44&shop_category_id=1&title=%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&exclude_filter=shop_category_id",
    "샌들/슬리퍼": "https://kream.co.kr/search?tab=44&shop_category_id=37&title=%EC%83%8C%EB%93%A4/%EC%8A%AC%EB%A6%AC%ED%8D%BC&exclude_filter=shop_category_id",
    "플랫": "https://kream.co.kr/search?tab=44&shop_category_id=70&title=%ED%94%8C%EB%9E%AB&exclude_filter=shop_category_id",
    "로퍼": "https://kream.co.kr/search?tab=44&shop_category_id=69&title=%EB%A1%9C%ED%8D%BC&exclude_filter=shop_category_id",
    "더비/레이스업": "https://kream.co.kr/search?tab=44&shop_category_id=55&title=%EB%8D%94%EB%B9%84/%EB%A0%88%EC%9D%B4%EC%8A%A4%EC%97%85&exclude_filter=shop_category_id",
    "힐/펌프스": "https://kream.co.kr/search?tab=44&shop_category_id=62&title=%ED%9E%90/%ED%8E%8C%ED%94%84%EC%8A%A4&exclude_filter=shop_category_id",
    "부츠": "https://kream.co.kr/search?tab=44&shop_category_id=35&title=%EB%B6%80%EC%B8%A0&exclude_filter=shop_category_id",
    "기타신발": "https://kream.co.kr/search?tab=44&shop_category_id=71&title=%EA%B8%B0%ED%83%80+%EC%8B%A0%EB%B0%9C&exclude_filter=shop_category_id",

    # BAG
    "미니백": "https://kream.co.kr/search?tab=63&shop_category_id=81&title=%EB%AF%B8%EB%8B%88%EB%B0%B1&exclude_filter=shop_category_id",
    "백팩": "https://kream.co.kr/search?tab=63&shop_category_id=82&title=%EB%B0%B1%ED%8C%A9&exclude_filter=shop_category_id",
    "숄더백": "https://kream.co.kr/search?tab=63&shop_category_id=84&title=%EC%88%84%EB%8D%94%EB%B0%B1&exclude_filter=shop_category_id",
    "토트백": "https://kream.co.kr/search?tab=63&shop_category_id=87&title=%ED%86%A0%ED%8A%B8%EB%B0%B1&exclude_filter=shop_category_id",
    "크로스백": "https://kream.co.kr/search?tab=63&shop_category_id=83&title=%ED%81%AC%EB%A1%9C%EC%8A%A4%EB%B0%B1&exclude_filter=shop_category_id",
    "클러치": "https://kream.co.kr/search?tab=63&shop_category_id=86&title=%ED%81%B4%EB%9F%AC%EC%B9%98&exclude_filter=shop_category_id",
    "더플백": "https://kream.co.kr/search?tab=63&shop_category_id=85&title=%EB%8D%94%ED%94%8C%EB%B0%B1&exclude_filter=shop_category_id",
    "에코백": "https://kream.co.kr/search?tab=63&shop_category_id=88&title=%EC%97%90%EC%BD%94%EB%B0%B1&exclude_filter=shop_category_id",
    "캐리어": "https://kream.co.kr/search?tab=63&shop_category_id=89&title=%EC%BA%90%EB%A6%AC%EC%96%B4&exclude_filter=shop_category_id",
    "기타 가방": "https://kream.co.kr/search?tab=63&shop_category_id=90&title=%EA%B8%B0%ED%83%80+%EA%B0%80%EB%B0%A9&exclude_filter=shop_category_id",

    # DRESS
    "원피스": "https://kream.co.kr/search?tab=50&shop_category_id=77&title=%EC%9B%90%ED%94%BC%EC%8A%A4&exclude_filter=shop_category_id",
    "점프수트": "https://kream.co.kr/search?tab=50&shop_category_id=197&title=%EC%A0%90%ED%94%84%EC%88%98%ED%8A%B8&exclude_filter=shop_category_id",
    "수트": "https://kream.co.kr/search?tab=50&shop_category_id=199&title=%EC%88%98%ED%8A%B8&exclude_filter=shop_category_id",
    "홈웨어": "https://kream.co.kr/search?tab=50&shop_category_id=198&title=%ED%99%88%EC%9B%A8%EC%96%B4&exclude_filter=shop_category_id",

    # HAT (새로운 대분류)
    "볼캡": "https://kream.co.kr/search?tab=46&shop_category_id=105&title=%EB%B3%BC%EC%BA%A1&exclude_filter=shop_category_id",
    "캠프캡": "https://kream.co.kr/search?tab=46&shop_category_id=201&title=%EC%BA%A0%ED%94%84%EC%BA%A1&exclude_filter=shop_category_id",
    "비니": "https://kream.co.kr/search?tab=46&shop_category_id=103&title=%EB%B9%84%EB%8B%88&exclude_filter=shop_category_id",
    "버킷햇": "https://kream.co.kr/search?tab=46&shop_category_id=104&title=%EB%B2%84%ED%82%B7%ED%96%87&exclude_filter=shop_category_id",
    "트루퍼햇": "https://kream.co.kr/search?tab=46&shop_category_id=202&title=%ED%8A%B8%EB%A3%A8%ED%8D%BC%ED%96%87&exclude_filter=shop_category_id",
    "바라클라바": "https://kream.co.kr/search?tab=46&shop_category_id=203&title=%EB%B0%94%EB%9D%BC%ED%81%B4%EB%9D%BC%EB%B0%94&exclude_filter=shop_category_id",
    "기타 모자": "https://kream.co.kr/search?tab=46&shop_category_id=106&title=%EA%B8%B0%ED%83%80+%EB%AA%A8%EC%9E%90&exclude_filter=shop_category_id",
}

# ===============================
# 카테고리 매핑: KREAM 카테고리 → (대분류, 중분류, 원본카테고리명)
# ===============================
CATEGORY_MAPPING = {
    # OUTER
    "패딩": ("OUTER", "PADDING", "패딩"),
    "코트": ("OUTER", "COAT", "코트"),
    "재킷": ("OUTER", "JACKET", "재킷"),
    "플리스": ("OUTER", "FLEECE", "플리스"),
    "베스트": ("OUTER", "VEST", "베스트"),
    "바람막이": ("OUTER", "JACKET", "바람막이"),
    "경량 패딩": ("OUTER", "PADDING", "경량 패딩"),
    "플리스 자켓": ("OUTER", "FLEECE_JACKET", "플리스 자켓"),
    "숏 패딩": ("OUTER", "PADDING", "숏 패딩"),
    "트레이닝 자켓": ("OUTER", "JACKET", "트레이닝 자켓"),
    "후드 자켓": ("OUTER", "JACKET", "후드 자켓"),
    "블루종": ("OUTER", "JACKET", "블루종"),
    "아노락": ("OUTER", "JACKET", "아노락"),
    "바시티 자켓": ("OUTER", "JACKET", "바시티 자켓"),
    "블레이저": ("OUTER", "JACKET", "블레이저"),
    "데님 자켓": ("OUTER", "JACKET", "데님 자켓"),
    "워크 자켓": ("OUTER", "JACKET", "워크 자켓"),
    "레더 자켓": ("OUTER", "JACKET", "레더 자켓"),
    "코치 자켓": ("OUTER", "JACKET", "코치 자켓"),
    "퍼 자켓": ("OUTER", "JACKET", "퍼 자켓"),
    "오버셔츠": ("OUTER", "JACKET", "오버셔츠"),
    "기타 자켓": ("OUTER", "JACKET", "기타 자켓"),
    "롱 코트": ("OUTER", "COAT", "롱 코트"),
    "숏 코트": ("OUTER", "COAT", "숏 코트"),
    "롱 패딩": ("OUTER", "PADDING", "롱 패딩"),
    "퀼팅 자켓": ("OUTER", "JACKET", "퀼팅 자켓"),
    "패딩 베스트": ("OUTER", "VEST", "패딩 베스트"),
    "트렌치 코트": ("OUTER", "COAT", "트렌치 코트"),
    "기타 아우터": ("OUTER", "ETC_OUTER", "기타 아우터"),

    # TOP
    "맨투맨": ("TOP", "SWEATSHIRT", "맨투맨"),
    "긴소매 후드티": ("TOP", "HOODIE", "긴소매 후드티"),
    "반팔 티셔츠": ("TOP", "TSHIRT", "반팔 티셔츠"),
    "긴팔 티셔츠": ("TOP", "TSHIRT", "긴팔 티셔츠"),
    "셔츠/블라우스": ("TOP", "SHIRT_BLOUSE", "셔츠/블라우스"),
    "니트/스웨터": ("TOP", "KNIT", "니트/스웨터"),
    "후드": ("TOP", "HOODIE", "후드"),
    "긴소매 티셔츠": ("TOP", "TSHIRT", "긴소매 티셔츠"),
    "후드 집업": ("TOP", "HOODIE", "후드 집업"),
    "스웨트셔츠": ("TOP", "SWEATSHIRT", "스웨트셔츠"),
    "반소매 티셔츠": ("TOP", "TSHIRT", "반소매 티셔츠"),
    "반소매 카라 티셔츠": ("TOP", "TSHIRT", "반소매 카라 티셔츠"),
    "긴소매 카라 티셔츠": ("TOP", "TSHIRT", "긴소매 카라 티셔츠"),
    "반소매 셔츠": ("TOP", "SHIRT_BLOUSE", "반소매 셔츠"),
    "긴소매 셔츠": ("TOP", "SHIRT_BLOUSE", "긴소매 셔츠"),
    "가디건": ("TOP", "KNIT", "가디건"),
    "크루넥 니트": ("TOP", "KNIT", "크루넥 니트"),
    "브이넥 니트": ("TOP", "KNIT", "브이넥 니트"),
    "터틀넥 니트": ("TOP", "KNIT", "터틀넥 니트"),
    "니트 베스트": ("TOP", "KNIT", "니트 베스트"),
    "블라우스": ("TOP", "SHIRT_BLOUSE", "블라우스"),
    "슬리브리스": ("TOP", "ETC_TOP", "슬리브리스"),
    "수영복": ("TOP", "ETC_TOP", "수영복"),
    "기타 상의": ("TOP", "ETC_TOP", "기타 상의"),
    

    # BOTTOM
    "데님": ("BOTTOM", "DENIM", "데님"),
    "슬랙스": ("BOTTOM", "SLACKS", "슬랙스"),
    "코튼 팬츠": ("BOTTOM", "COTTON_PANTS", "코튼 팬츠"),
    "트레이닝 팬츠": ("BOTTOM", "TRAINING_PANTS", "트레이닝 팬츠"),
    "반바지": ("BOTTOM", "SHORTS", "반바지"),
    "스커트": ("BOTTOM", "SKIRT", "스커트"),
    "레깅스": ("BOTTOM", "LEGGINGS", "레깅스"),
    "숏 팬츠": ("BOTTOM", "SHORTS", "숏 팬츠"),
    "스웨트팬츠": ("BOTTOM", "TRAINING_PANTS", "스웨트팬츠"),
    "데님 팬츠": ("BOTTOM", "DENIM", "데님 팬츠"),
    "카고 팬츠": ("BOTTOM", "COTTON_PANTS", "카고 팬츠"),
    "데님 스커트": ("BOTTOM", "SKIRT", "데님 스커트"),
    "미니 스커트": ("BOTTOM", "SKIRT", "미니 스커트"),
    "미디 스커트": ("BOTTOM", "SKIRT", "미디 스커트"),
    "롱 스커트": ("BOTTOM", "SKIRT", "롱 스커트"),
    "오버올": ("BOTTOM", "ETC_BOTTOM", "오버올"),
    "기타 하의": ("BOTTOM", "ETC_BOTTOM", "기타 하의"),

    # SHOES
    "스니커즈": ("SHOES", "SNEAKERS", "스니커즈"),
    "부츠": ("SHOES", "BOOTS", "부츠"),
    "로퍼": ("SHOES", "LOAFER", "로퍼"),
    "샌들/슬리퍼": ("SHOES", "SANDAL_SLIPPER", "샌들/슬리퍼"),
    "스포츠화": ("SHOES", "SPORTS_SHOES", "스포츠화"),
    "플랫": ("SHOES", "ETC_SHOES", "플랫"),
    "더비/레이스업": ("SHOES", "ETC_SHOES", "더비/레이스업"),
    "힐/펌프스": ("SHOES", "ETC_SHOES", "힐/펌프스"),
    "기타 신발": ("SHOES", "ETC_SHOES", "기타 신발"),

    # BAG
    "백팩": ("BAG", "BACKPACK", "백팩"),
    "크로스백": ("BAG", "CROSSBODY", "크로스백"),
    "숄더백": ("BAG", "SHOULDER", "숄더백"),
    "토트백": ("BAG", "TOTE", "토트백"),
    "클러치": ("BAG", "CLUTCH", "클러치"),
    "미니백": ("BAG", "ETC_BAG", "미니백"),
    "더플백": ("BAG", "ETC_BAG", "더플백"),
    "에코백": ("BAG", "TOTE", "에코백"),
    "캐리어": ("BAG", "ETC_BAG", "캐리어"),
    "기타 가방": ("BAG", "ETC_BAG", "기타 가방"),
    
    # DRESS
    "원피스": ("DRESS", "ONE_PIECE", "원피스"),
    "세트업": ("DRESS", "SETUP", "세트업"),
    "점프수트": ("DRESS", "SETUP", "점프수트"),
    "수트": ("DRESS", "SETUP", "수트"),
    "홈웨어": ("DRESS", "SETUP", "홈웨어"),
    
    # HAT
    "캡": ("HAT", "CAP", "캡"),
    "볼캡": ("HAT", "CAP", "볼캡"),
    "캠프캡": ("HAT", "CAP", "캠프캡"),
    "비니": ("HAT", "BEANIE", "비니"),
    "발라클라바": ("HAT", "BALACLAVA", "발라클라바"),
    "바라클라바": ("HAT", "BALACLAVA", "바라클라바"),
    "트루퍼햇": ("HAT", "TROOPER", "트루퍼햇"),
    "페도라": ("HAT", "FEDORA", "페도라"),
    "베레모": ("HAT", "BERET", "베레모"),
    "버킷햇": ("HAT", "ETC_HAT", "버킷햇"),
    "기타 모자": ("HAT", "ETC_HAT", "기타 모자"),
}


# 페이지 설정
PAGE_WAIT_RANGE = (2.5, 4.5)        # 페이지 로드 후 대기
CURSOR_WAIT_RANGE = (1.5, 3.0)      # cursor 이동 전 대기
CATEGORY_WAIT_RANGE = (6.0, 10.0)   # 카테고리 변경 시 대기
SCROLL_WAIT_RANGE = (0.8, 1.5)


# ===============================
# 유틸
# ===============================
def only_digits(s: str) -> str:
    return re.sub(r"[^\d]", "", s or "")

def set_cursor(url: str, cursor_num: int) -> str:
    u = urlparse(url)
    q = parse_qs(u.query)
    q["cursor"] = [str(cursor_num)]
    return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, doseq=True), u.fragment))

def human_sleep(rng):
    time.sleep(random.uniform(*rng))

# ===============================
# DOM에서 상품 데이터 추출
# ===============================
JS_EXTRACT = r"""
() => {
  const results = [];
  const cards = document.querySelectorAll("div.product_card");

  for (const card of cards) {
    const a = card.querySelector("a.item_inner");
    if (!a) continue;

    const href = a.getAttribute("href") || "";
    if (!href.includes("/products/")) continue;

    // 브랜드
    const brand = (card.querySelector(".product_info_brand .brand-name")?.textContent || "").trim();

    // 상품명 (번역명 우선, 없으면 원명)
    const name =
      (card.querySelector(".product_info_product_name .translated_name")?.textContent || "").trim()
      || (card.querySelector(".product_info_product_name .name")?.textContent || "").trim();

    // 이미지
    const img = card.querySelector("picture.product_img img");
    const imgUrl = (img?.getAttribute("src") || "").trim();

    // 가격: "134,000원" 형태
    const priceText = (card.querySelector(".price_area .amount span")?.textContent || "").trim();
    const price = priceText.replace(/[^\d]/g, "");

    results.push({
      href,
      brand,
      name,
      imgUrl,
      price,
    });
  }

  return results;
}
"""

# ===============================
# 상품 대기
# ===============================
def wait_for_products(page):
    page.wait_for_selector("div.product_card a.item_inner", timeout=60000)

# ===============================
# 메인 크롤러
# ===============================
def scrape():
    data_by_major = {
        "TOP": [],
        "OUTER": [],
        "BOTTOM": [],
        "DRESS": [],
        "BAG": [],
        "SHOES": [],
        "HAT": [],
    }

    global_seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=120   # ⭐ 핵심: 액션 자체를 느리게
        )

        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        # 리소스 일부 차단
        def block(route, request):
            if request.resource_type in ["font", "media"]:
                return route.abort()
            return route.continue_()

        page.route("**/*", block)

        for category_name, base_url in CATEGORIES.items():
            if category_name not in CATEGORY_MAPPING:
                continue

            large, middle, origin = CATEGORY_MAPPING[category_name]
            print(f"\n📂 START: {large} > {middle} > {origin}")

            cursor = 1
            category_count = 0

            human_sleep(CATEGORY_WAIT_RANGE)

            while category_count < TARGET_PER_CATEGORY:
                human_sleep(CURSOR_WAIT_RANGE)
                url = set_cursor(base_url, cursor)

                print(f"  ▶ cursor={cursor}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    wait_for_products(page)
                    human_sleep(PAGE_WAIT_RANGE)
                except Exception as e:
                    print(f"  ❌ 페이지 실패: {e}")
                    break

                snapshot = page.evaluate(JS_EXTRACT)
                added = 0

                for it in snapshot:
                    href = (it.get("href") or "").strip()
                    if not href:
                        continue

                    full_url = urljoin(BASE, href)
                    if full_url in global_seen:
                        continue

                    global_seen.add(full_url)
                    added += 1
                    category_count += 1

                    data_by_major[large].append([
                        large,
                        middle,
                        origin,
                        it.get("name", "") or "",
                        it.get("brand", "") or "",
                        "",
                        only_digits(it.get("price", "")),
                        "",
                        full_url,
                        it.get("imgUrl", "") or "",
                    ])

                print(f"    +{added} (누적 {category_count})")

                if added == 0:
                    print("    ⚠️ 더 이상 로드 없음 → 종료")
                    break

                cursor += 1

            print(f"✅ END: {origin} ({category_count}개)")

        browser.close()

    # ===============================
    # 대분류별 CSV 저장 (헤더 ❌)
    # ===============================
    total = 0
    for major, rows in data_by_major.items():
        if not rows:
            continue

        path = os.path.join(OUTPUT_DIR, f"{major}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"✅ kream/{major}.csv 저장 ({len(rows)}개)")
        total += len(rows)

    print(f"\n🎉 KREAM 전체 완료 (총 {total}개)")


if __name__ == "__main__":
    scrape()