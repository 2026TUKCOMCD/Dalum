from playwright.sync_api import sync_playwright
import csv
import time
import re
import random
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

# ===============================
# 설정
# ===============================
TARGET_PER_CATEGORY = 999999
OUTPUT_DIR = "kream_products"

# 봇 감지 회피를 위한 설정
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# 페이지 설정
PAGE_LOAD_WAIT_MIN = 3.0
PAGE_LOAD_WAIT_MAX = 6.0
REQUEST_DELAY_MIN = 3.0
REQUEST_DELAY_MAX = 5.0

# 재시도 설정
MAX_RETRIES = 5
RETRY_DELAY = 10

# ===============================
# 카테고리 매핑
# ===============================
CATEGORY_MAPPING = {
    # SHOES 카테고리
    "스니커즈": ("SHOES", "SNEAKERS", "스니커즈"),
    "샌들/슬리퍼": ("SHOES", "SANDAL_SLIPPER", "샌들/슬리퍼"),
    "플랫": ("SHOES", "ETC_SHOES", "플랫"),
    "로퍼": ("SHOES", "LOAFER", "로퍼"),
    "더비/레이스업": ("SHOES", "ETC_SHOES", "더비/레이스업"),
    "힐/펌프스": ("SHOES", "ETC_SHOES", "힐/펌프스"),
    "부츠": ("SHOES", "BOOTS", "부츠"),
    "기타 신발": ("SHOES", "ETC_SHOES", "기타 신발"),
    
    # OUTER 카테고리
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
    "베스트": ("OUTER", "VEST", "베스트"),
    "오버셔츠": ("OUTER", "JACKET", "오버셔츠"),
    "기타 자켓": ("OUTER", "JACKET", "기타 자켓"),
    "롱 코트": ("OUTER", "COAT", "롱 코트"),
    "숏 코트": ("OUTER", "COAT", "숏 코트"),
    "롱 패딩": ("OUTER", "PADDING", "롱 패딩"),
    "퀼팅 자켓": ("OUTER", "JACKET", "퀼팅 자켓"),
    "패딩 베스트": ("OUTER", "VEST", "패딩 베스트"),
    "트렌치 코트": ("OUTER", "COAT", "트렌치 코트"),
    "기타 아우터": ("OUTER", "ETC_OUTER", "기타 아우터"),
    
    # TOP 카테고리
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
    "원피스": ("DRESS", "ONE_PIECE", "원피스"),
    "점프수트": ("DRESS", "SETUP", "점프수트"),
    "수트": ("DRESS", "SETUP", "수트"),
    "기타 상의": ("TOP", "ETC_TOP", "기타 상의"),
    
    # BOTTOM 카테고리
    "숏 팬츠": ("BOTTOM", "SHORTS", "숏 팬츠"),
    "스웨트팬츠": ("BOTTOM", "TRAINING_PANTS", "스웨트팬츠"),
    "트레이닝 팬츠": ("BOTTOM", "TRAINING_PANTS", "트레이닝 팬츠"),
    "데님 팬츠": ("BOTTOM", "DENIM", "데님 팬츠"),
    "카고 팬츠": ("BOTTOM", "COTTON_PANTS", "카고 팬츠"),
    "코튼 팬츠": ("BOTTOM", "COTTON_PANTS", "코튼 팬츠"),
    "슬랙스": ("BOTTOM", "SLACKS", "슬랙스"),
    "레깅스": ("BOTTOM", "LEGGINGS", "레깅스"),
    "데님 스커트": ("BOTTOM", "SKIRT", "데님 스커트"),
    "미니 스커트": ("BOTTOM", "SKIRT", "미니 스커트"),
    "미디 스커트": ("BOTTOM", "SKIRT", "미디 스커트"),
    "롱 스커트": ("BOTTOM", "SKIRT", "롱 스커트"),
    "오버올": ("BOTTOM", "ETC_BOTTOM", "오버올"),
    "기타 하의": ("BOTTOM", "ETC_BOTTOM", "기타 하의"),
    
    # BAG 카테고리
    "미니백": ("BAG", "ETC_BAG", "미니백"),
    "백팩": ("BAG", "BACKPACK", "백팩"),
    "숄더백": ("BAG", "SHOULDER", "숄더백"),
    "토트백": ("BAG", "TOTE", "토트백"),
    "크로스백": ("BAG", "CROSSBODY", "크로스백"),
    "클러치": ("BAG", "CLUTCH", "클러치"),
    "더플백": ("BAG", "ETC_BAG", "더플백"),
    "에코백": ("BAG", "TOTE", "에코백"),
    "캐리어": ("BAG", "ETC_BAG", "캐리어"),
    "기타 가방": ("BAG", "ETC_BAG", "기타 가방"),
    
    # HAT 카테고리
    "볼캡": ("HAT", "CAP", "볼캡"),
    "캠프캡": ("HAT", "CAP", "캠프캡"),
    "비니": ("HAT", "BEANIE", "비니"),
    "버킷햇": ("HAT", "ETC_HAT", "버킷햇"),
    "트루퍼햇": ("HAT", "TROOPER", "트루퍼햇"),
    "바라클라바": ("HAT", "BALACLAVA", "바라클라바"),
    "기타 모자": ("HAT", "ETC_HAT", "기타 모자"),
}

# ===============================
# 카테고리 URL (여기에 크림 URL을 채워주세요)
# ===============================
CATEGORIES = {
    # SHOES
    "스니커즈": "https://kream.co.kr/search?tab=44&shop_category_id=1&title=%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&exclude_filter=shop_category_id",  
    "샌들/슬리퍼": "https://kream.co.kr/search?tab=44&shop_category_id=37&title=%EC%83%8C%EB%93%A4/%EC%8A%AC%EB%A6%AC%ED%8D%BC&exclude_filter=shop_category_id",
    "플랫": "https://kream.co.kr/search?tab=44&shop_category_id=70&title=%ED%94%8C%EB%9E%AB&exclude_filter=shop_category_id",
    "로퍼": "https://kream.co.kr/search?tab=44&shop_category_id=69&title=%EB%A1%9C%ED%8D%BC&exclude_filter=shop_category_id",
    "더비/레이스업": "https://kream.co.kr/search?tab=44&shop_category_id=55&title=%EB%8D%94%EB%B9%84/%EB%A0%88%EC%9D%B4%EC%8A%A4%EC%97%85&exclude_filter=shop_category_id",
    "힐/펌프스": "https://kream.co.kr/search?tab=44&shop_category_id=62&title=%ED%9E%90/%ED%8E%8C%ED%94%84%EC%8A%A4&exclude_filter=shop_category_id",
    "부츠": "https://kream.co.kr/search?tab=44&shop_category_id=35&title=%EB%B6%80%EC%B8%A0&exclude_filter=shop_category_id",
    "기타 신발": "https://kream.co.kr/search?tab=44&shop_category_id=71&title=%EA%B8%B0%ED%83%80+%EC%8B%A0%EB%B0%9C&exclude_filter=shop_category_id",
    
    # OUTER
    "바람막이": "https://kream.co.kr/search?tab=49&shop_category_id=22&title=%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4&exclude_filter=shop_category_id",
    "경량 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=150&title=%EA%B2%BD%EB%9F%89+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "플리스 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=162&title=%ED%94%8C%EB%A6%AC%EC%8A%A4+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "숏 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=20&title=%EC%88%8F+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "트레이닝 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=165&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "후드 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=161&title=%ED%9B%84%EB%93%9C+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "블루종": "https://kream.co.kr/search?tab=49&shop_category_id=154&title=%EB%B8%94%EB%A3%A8%EC%A2%85&exclude_filter=shop_category_id",
    "아노락": "https://kream.co.kr/search?tab=49&shop_category_id=72&title=%EC%95%84%EB%85%B8%EB%9D%BD&exclude_filter=shop_category_id",
    "바시티 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=169&title=%EB%B0%94%EC%8B%9C%ED%8B%B0+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "블레이저": "https://kream.co.kr/search?tab=49&shop_category_id=156&title=%EB%B8%94%EB%A0%88%EC%9D%B4%EC%A0%80&exclude_filter=shop_category_id",
    "데님 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=166&title=%EB%8D%B0%EB%8B%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "워크 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=158&title=%EC%9B%8C%ED%81%AC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "레더 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=164&title=%EB%A0%88%EB%8D%94+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "코치 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=168&title=%EC%BD%94%EC%B9%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "퍼 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=160&title=%ED%8D%BC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "베스트": "https://kream.co.kr/search?tab=49&shop_category_id=153&title=%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "오버셔츠": "https://kream.co.kr/search?tab=49&shop_category_id=167&title=%EC%98%A4%EB%B2%84%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "기타 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=159&title=%EA%B8%B0%ED%83%80+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "롱 코트": "https://kream.co.kr/search?tab=49&shop_category_id=21&title=%EB%A1%B1+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "숏 코트": "https://kream.co.kr/search?tab=49&shop_category_id=163&title=%EC%88%8F+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "롱 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=149&title=%EB%A1%B1+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "퀼팅 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=157&title=%ED%80%BC%ED%8C%85+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "패딩 베스트": "https://kream.co.kr/search?tab=49&shop_category_id=152&title=%ED%8C%A8%EB%94%A9+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "트렌치 코트": "https://kream.co.kr/search?tab=49&shop_category_id=151&title=%ED%8A%B8%EB%A0%8C%EC%B9%98+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "기타 아우터": "https://kream.co.kr/search?tab=49&shop_category_id=73&title=%EA%B8%B0%ED%83%80+%EC%95%84%EC%9A%B0%ED%84%B0&exclude_filter=shop_category_id",
    
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
    "크루넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=195&title=%ED%81%AC%EB%A3%A8%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "브이넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=193&title=%EB%B8%8C%EC%9D%B4%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "터틀넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=194&title=%ED%84%B0%ED%8B%80%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "니트 베스트": "https://kream.co.kr/search?tab=50&shop_category_id=196&title=%EB%8B%88%ED%8A%B8+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "블라우스": "https://kream.co.kr/search?tab=50&shop_category_id=192&title=%EB%B8%94%EB%9D%BC%EC%9A%B0%EC%8A%A4&exclude_filter=shop_category_id",
    "슬리브리스": "https://kream.co.kr/search?tab=50&shop_category_id=76&title=%EC%8A%AC%EB%A6%AC%EB%B8%8C%EB%A6%AC%EC%8A%A4&exclude_filter=shop_category_id",
    "원피스": "https://kream.co.kr/search?tab=50&shop_category_id=77&title=%EC%9B%90%ED%94%BC%EC%8A%A4&exclude_filter=shop_category_id",
    "점프수트": "https://kream.co.kr/search?tab=50&shop_category_id=197&title=%EC%A0%90%ED%94%84%EC%88%98%ED%8A%B8&exclude_filter=shop_category_id",
    "수트": "https://kream.co.kr/search?tab=50&shop_category_id=199&title=%EC%88%98%ED%8A%B8&exclude_filter=shop_category_id",
    "기타 상의": "https://kream.co.kr/search?tab=50&shop_category_id=78&title=%EA%B8%B0%ED%83%80+%EC%83%81%EC%9D%98&exclude_filter=shop_category_id",
    
    # BOTTOM
    "숏 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=175&title=%EC%88%8F+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "스웨트팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=176&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "트레이닝 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=177&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "데님 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=173&title=%EB%8D%B0%EB%8B%98+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "카고 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=174&title=%EC%B9%B4%EA%B3%A0+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "코튼 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=178&title=%EC%BD%94%ED%8A%BC+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "슬랙스": "https://kream.co.kr/search?tab=51&shop_category_id=179&title=%EC%8A%AC%EB%9E%99%EC%8A%A4&exclude_filter=shop_category_id",
    "레깅스": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "데님 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "미니 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "미디 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=181&title=%EB%AF%B8%EB%94%94+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "롱 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=182&title=%EB%A1%B1+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "오버올": "https://kream.co.kr/search?tab=51&shop_category_id=183&title=%EC%98%A4%EB%B2%84%EC%98%AC&exclude_filter=shop_category_id",
    "기타 하의": "https://kream.co.kr/search?tab=51&shop_category_id=80&title=%EA%B8%B0%ED%83%80+%ED%95%98%EC%9D%98&exclude_filter=shop_category_id",
    
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
    
    # HAT
    "볼캡": "https://kream.co.kr/search?tab=46&shop_category_id=105&title=%EB%B3%BC%EC%BA%A1&exclude_filter=shop_category_id",
    "캠프캡": "https://kream.co.kr/search?tab=46&shop_category_id=201&title=%EC%BA%A0%ED%94%84%EC%BA%A1&exclude_filter=shop_category_id",
    "비니": "https://kream.co.kr/search?tab=46&shop_category_id=103&title=%EB%B9%84%EB%8B%88&exclude_filter=shop_category_id",
    "버킷햇": "https://kream.co.kr/search?tab=46&shop_category_id=104&title=%EB%B2%84%ED%82%B7%ED%96%87&exclude_filter=shop_category_id",
    "트루퍼햇": "https://kream.co.kr/search?tab=46&shop_category_id=202&title=%ED%8A%B8%EB%A3%A8%ED%8D%BC%ED%96%87&exclude_filter=shop_category_id",
    "바라클라바": "https://kream.co.kr/search?tab=46&shop_category_id=203&title=%EB%B0%94%EB%9D%BC%ED%81%B4%EB%9D%BC%EB%B0%94&exclude_filter=shop_category_id",
    "기타 모자": "https://kream.co.kr/search?tab=46&shop_category_id=106&title=%EA%B8%B0%ED%83%80+%EB%AA%A8%EC%9E%90&exclude_filter=shop_category_id",
}

BASE = "https://kream.co.kr"

# ===============================
# 유틸 함수들
# ===============================
def only_digits(s: str) -> str:
    return re.sub(r"[^\d]", "", s or "")

def set_cursor(url: str, cursor_num: int) -> str:
    u = urlparse(url)
    q = parse_qs(u.query)
    q["cursor"] = [str(cursor_num)]
    return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, doseq=True), u.fragment))

JS_EXTRACT = r"""
() => {
  const results = [];
  const cards = document.querySelectorAll("div.product_card");

  for (const card of cards) {
    const a = card.querySelector("a.item_inner");
    if (!a) continue;

    const href = a.getAttribute("href") || "";
    if (!href.includes("/products/")) continue;

    const brand = (card.querySelector(".product_info_brand .brand-name")?.textContent || "").trim();
    const name =
      (card.querySelector(".product_info_product_name .translated_name")?.textContent || "").trim()
      || (card.querySelector(".product_info_product_name .name")?.textContent || "").trim();
    const img = card.querySelector("picture.product_img img");
    const imgUrl = (img?.getAttribute("src") || "").trim();
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

def wait_for_products(page, timeout=30000):
    """상품 카드가 로드될 때까지 대기"""
    try:
        page.wait_for_selector("div.product_card a.item_inner", timeout=timeout)
        return True
    except:
        return False

def random_delay(min_sec=REQUEST_DELAY_MIN, max_sec=REQUEST_DELAY_MAX):
    time.sleep(random.uniform(min_sec, max_sec))

def human_like_scroll(page):
    try:
        scroll_count = random.randint(3, 6)
        for _ in range(scroll_count):
            scroll_amount = random.randint(200, 600)
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.2))
        
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(random.uniform(0.8, 1.5))
    except:
        pass

def random_mouse_movement(page):
    try:
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 1200)
            y = random.randint(100, 700)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.2, 0.5))
    except:
        pass

def check_for_captcha(page):
    """CAPTCHA 또는 차단 페이지 감지"""
    try:
        content = page.content()
        if "일시적인 서비스 장애" in content or "reCAPTCHA" in content or "로봇이 아닙니다" in content:
            print("  🚫 CAPTCHA 또는 차단 페이지 감지됨!")
            return True
    except:
        pass
    return False

def scrape():
    data_by_category = {
        "SHOES": [],
        "OUTER": [],
        "TOP": [],
        "BOTTOM": [],
        "DRESS": [],
        "BAG": [],
        "HAT": []
    }
    
    global_seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=200,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--window-size=1400,900',
                '--start-maximized',
            ]
        )
        
        user_agent = random.choice(USER_AGENTS)
        
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=user_agent,
            locale='ko-KR',
            timezone_id='Asia/Seoul',
            extra_http_headers={
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }
        )
        
        page = context.new_page()

        # 자동화 감지 우회
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.navigator.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ko-KR', 'ko', 'en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'platform', {
                get: () => 'MacIntel'
            });
            
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.'
            });
        """)

        # 리소스 차단
        def block(route, request):
            if request.resource_type in ["font", "media"]:
                return route.abort()
            return route.continue_()
        page.route("**/*", block)

        print("🔄 초기 페이지 방문 중...")
        try:
            page.goto("https://kream.co.kr", wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(5, 8))
            human_like_scroll(page)
        except Exception as e:
            print(f"⚠️ 초기 페이지 로딩 실패: {e}")
        
        for category_name, base_url in CATEGORIES.items():
            # URL이 비어있으면 건너뛰기
            if not base_url:
                print(f"⚠️ '{category_name}' 카테고리의 URL이 설정되지 않았습니다. 건너뜁니다.")
                continue
                
            if category_name not in CATEGORY_MAPPING:
                print(f"⚠️ '{category_name}' 카테고리가 CATEGORY_MAPPING에 없습니다.")
                continue
            
            large_cat, medium_cat, original_cat = CATEGORY_MAPPING[category_name]
            
            print(f"\n📂 카테고리 시작: {large_cat} > {medium_cat} > {original_cat}")
            category_count = 0
            cursor = 1
            max_pages = 9999
            consecutive_failures = 0

            for page_num in range(1, max_pages + 1):
                if category_count >= TARGET_PER_CATEGORY:
                    break
                
                # 연속 실패 시 긴 휴식
                if consecutive_failures >= 3:
                    print(f"  ⚠️ 연속 실패 {consecutive_failures}번, 60초 휴식...")
                    time.sleep(random.uniform(60, 90))
                    consecutive_failures = 0
                    
                    # 브라우저 재시작
                    if consecutive_failures >= 5:
                        print("  🔄 브라우저 재시작...")
                        page.close()
                        context.close()
                        browser.close()
                        time.sleep(10)
                        
                        browser = p.chromium.launch(
                            headless=False,
                            slow_mo=200,
                            args=[
                                '--disable-blink-features=AutomationControlled',
                                '--disable-dev-shm-usage',
                                '--no-sandbox',
                            ]
                        )
                        user_agent = random.choice(USER_AGENTS)
                        context = browser.new_context(
                            viewport={"width": 1400, "height": 900},
                            user_agent=user_agent,
                            locale='ko-KR',
                            timezone_id='Asia/Seoul',
                        )
                        page = context.new_page()
                        page.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            });
                        """)
                        page.route("**/*", block)
                        consecutive_failures = 0

                url = set_cursor(base_url, cursor)
                print(f"  ▶ cursor={cursor} 이동 (페이지 {page_num})")

                # 재시도 로직
                success = False
                for retry in range(MAX_RETRIES):
                    try:
                        random_delay()
                        
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        
                        # CAPTCHA 체크
                        if check_for_captcha(page):
                            print(f"  ⚠️ 차단됨! 60초 대기 후 재시도... (시도 {retry+1}/{MAX_RETRIES})")
                            time.sleep(random.uniform(60, 90))
                            continue
                        
                        if not wait_for_products(page, timeout=30000):
                            print(f"  ⚠️ 상품 로드 실패 (시도 {retry+1}/{MAX_RETRIES})")
                            time.sleep(RETRY_DELAY)
                            continue
                        
                        random_mouse_movement(page)
                        time.sleep(random.uniform(PAGE_LOAD_WAIT_MIN, PAGE_LOAD_WAIT_MAX))
                        human_like_scroll(page)
                        
                        success = True
                        consecutive_failures = 0
                        break
                        
                    except Exception as e:
                        print(f"  ❌ 시도 {retry+1}/{MAX_RETRIES} 실패: {e}")
                        if retry < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (retry + 1)
                            print(f"  ⏳ {wait_time}초 대기 후 재시도...")
                            time.sleep(wait_time)
                        else:
                            consecutive_failures += 1

                if not success:
                    print(f"  💀 모든 재시도 실패. 다음 페이지로...")
                    continue

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
                    category_count += 1
                    added += 1

                    row = {
                        "대분류": large_cat,
                        "중분류": medium_cat,
                        "카테고리": original_cat,
                        "상품명": it.get("name", "") or "",
                        "브랜드": it.get("brand", "") or "",
                        "정가": "",
                        "판매가": only_digits(it.get("price", "") or ""),
                        "할인율(%)": "",
                        "상품 URL": full_url,
                        "이미지 URL": it.get("imgUrl", "") or "",
                    }
                    
                    data_by_category[large_cat].append(row)

                    if category_count >= TARGET_PER_CATEGORY:
                        break

                print(f"    [{original_cat}] 누적: {category_count}개 (+{added})")

                if added == 0:
                    print(f"    ⚠️ cursor={cursor}에서 추가 0개 → 종료")
                    break

                cursor += 1
                
                # 페이지마다 더 긴 휴식
                if page_num % 5 == 0:
                    rest_time = random.uniform(30, 45)
                    print(f"  ☕ 5페이지 완료, {rest_time:.1f}초 휴식...")
                    time.sleep(rest_time)

            print(f"✅ END: {original_cat} (수집 {category_count}개)")
            
            # 카테고리 전환 시 더 긴 휴식
            time.sleep(random.uniform(15, 25))

        browser.close()

    # CSV 저장
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    fieldnames = [
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
    ]
    
    total_count = 0
    for large_cat, rows in data_by_category.items():
        if not rows:
            continue
            
        output_file = os.path.join(OUTPUT_DIR, f"{large_cat}.csv")
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            #writer.writeheader()
            writer.writerows(rows)
        
        total_count += len(rows)
        print(f"\n✅ {large_cat} CSV 저장 완료: {output_file} ({len(rows)}개)")

    print(f"\n✅ 전체 CSV 저장 완료: {OUTPUT_DIR}/ (총 {total_count}개)")


if __name__ == "__main__":
    scrape()