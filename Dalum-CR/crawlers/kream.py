from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import csv, time, re, random, os
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

TARGET_PER_CATEGORY = 10
OUTPUT_DIR = "kream_products"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
]

PAGE_LOAD_WAIT_MIN = 3.0
PAGE_LOAD_WAIT_MAX = 6.0
REQUEST_DELAY_MIN = 3.0
REQUEST_DELAY_MAX = 5.0
MAX_RETRIES = 5
RETRY_DELAY = 10

CATEGORY_MAPPING = {
    "스니커즈": ("SHOES", "SNEAKERS", "스니커즈"),
    "샌들/슬리퍼": ("SHOES", "SANDAL_SLIPPER", "샌들/슬리퍼"),
    "플랫": ("SHOES", "ETC_SHOES", "플랫"),
    "로퍼": ("SHOES", "LOAFER", "로퍼"),
    "더비/레이스업": ("SHOES", "ETC_SHOES", "더비/레이스업"),
    "힐/펌프스": ("SHOES", "ETC_SHOES", "힐/펌프스"),
    "부츠": ("SHOES", "BOOTS", "부츠"),
    "기타 신발": ("SHOES", "ETC_SHOES", "기타 신발"),
    "바람막이": ("OUTER", "JACKET", "바람막이"),
    "경량 패딩": ("OUTER", "PADDING", "경량 패딩"),
    "플리스 자켓": ("OUTER", "FLEECE_JACKET", "플리스 자켓"),
    "숏 패딩": ("OUTER", "PADDING", "숏 패딩"),
    "롱 패딩": ("OUTER", "PADDING", "롱 패딩"),
    "경량 패딩": ("OUTER", "PADDING", "경량 패딩"),
    #COAT
    "롱 코트": ("OUTER", "COAT", "롱 코트"),
    "숏 코트": ("OUTER", "COAT", "숏 코트"),
    "트렌치 코트": ("OUTER", "COAT", "트렌치 코트"),
    #JACKET
    "바시티 자켓": ("OUTER", "JACKET", "바시티 자켓"),
    "데님 자켓": ("OUTER", "JACKET", "데님 자켓"),
    "무스탕/퍼": ("OUTER", "JACKET", "무스탕/퍼"),
    "레더 자켓": ("OUTER", "JACKET", "레더 자켓"),
    "블레이저": ("OUTER", "JACKET", "블레이저"),
    "퀼팅 자켓": ("OUTER", "JACKET", "퀼팅 자켓"),
    "워크 자켓": ("OUTER", "JACKET", "워크 자켓"),
    "오버 셔츠": ("OUTER", "JACKET", "오버 셔츠"),
    "후드 자켓": ("OUTER", "JACKET", "후드 자켓"),
    "트레이닝 자켓": ("OUTER", "JACKET", "트레이닝 자켓"),
    "코치 자켓": ("OUTER", "JACKET", "코치 자켓"),
    "플리스 자켓": ("OUTER", "JACKET", "플리스 자켓"),
    "기타 자켓": ("OUTER", "JACKET", "기타 자켓"),
    #JUMPER
    "바람막이": ("OUTER", "JUMPER", "바람막이"),
    "블루종": ("OUTER", "JUMPER", "블루종"),
    "아노락": ("OUTER", "JUMPER", "아노락"),
    #VEST
    "베스트": ("OUTER", "VEST", "베스트"),
    "패딩 베스트": ("OUTER", "VEST", "패딩 베스트"),
    #CARDIGAN
    "가디건": ("TOP", "CARDIGAN", "가디건"),
    #ZIP_UP
    "후드 집업": ("TOP", "ZIP_UP", "후드 집업"),
    #ETC_OUTER
    "기타 아우터": ("OUTER", "ETC_OUTER", "기타 아우터"),
    "후드": ("TOP", "HOODIE", "후드"),
    #KNIT
    "크루넥 니트": ("TOP", "KNIT", "크루넥 니트"),
    "브이넥 니트": ("TOP", "KNIT", "브이넥 니트"),
    "터틀넥 니트": ("TOP", "KNIT", "터틀넥 니트"),
    "니트 베스트": ("TOP", "KNIT", "니트 베스트"),
    #BLOUSE
    "블라우스": ("TOP", "BLOUSE", "블라우스"),
    #ETC_TOP
    "기타 상의": ("TOP", "ETC_TOP", "기타 상의"),
    "숏 팬츠": ("BOTTOM", "SHORTS", "숏 팬츠"),
    "스웨트팬츠": ("BOTTOM", "TRAINING_PANTS", "스웨트팬츠"),
    "트레이닝 팬츠": ("BOTTOM", "TRAINING_PANTS", "트레이닝 팬츠"),
    "데님 팬츠": ("BOTTOM", "DENIM", "데님 팬츠"),
    #SLACKS
    "슬랙스": ("BOTTOM", "SLACKS", "슬랙스"),
    #PANTS
    "코튼 팬츠": ("BOTTOM", "PANTS", "코튼 팬츠"),
    "카고 팬츠": ("BOTTOM", "PANTS", "카고 팬츠"),
    "트레이닝 팬츠": ("BOTTOM", "PANTS", "트레이닝 팬츠"),
    "스웨트팬츠": ("BOTTOM", "PANTS", "스웨트팬츠"),
    #SHORTS
    "숏 팬츠": ("BOTTOM", "SHORTS", "숏 팬츠"),
    #SKIRT
    "데님 스커트": ("BOTTOM", "SKIRT", "데님 스커트"),
    "미니 스커트": ("BOTTOM", "SKIRT", "미니 스커트"),
    "미디 스커트": ("BOTTOM", "SKIRT", "미디 스커트"),
    "롱 스커트": ("BOTTOM", "SKIRT", "롱 스커트"),
    #ETC_BOTTOM
    "기타 하의": ("BOTTOM", "ETC_BOTTOM", "기타 하의"),
    "미니백": ("BAG", "ETC_BAG", "미니백"),
    "백팩": ("BAG", "BACKPACK", "백팩"),
    #CROSSBODY
    "크로스백": ("BAG", "CROSSBODY", "크로스백"),
    "숄더백": ("BAG", "SHOULDER", "숄더백"),
    #TOTE
    "토트백": ("BAG", "TOTE", "토트백"),
    "에코백": ("BAG", "TOTE", "에코백"),
    #ETC_BAG
    "미니백": ("BAG", "ETC_BAG", "미니백"),
    "더플백": ("BAG", "ETC_BAG", "더플백"),
    "클러치": ("BAG", "ETC_BAG", "클러치"),
    "기타 가방": ("BAG", "ETC_BAG", "기타 가방"),
    "볼캡": ("HAT", "CAP", "볼캡"),
    "캠프캡": ("HAT", "CAP", "캠프캡"),
    #BEANIE
    "비니": ("HAT", "BEANIE", "비니"),
    #BALACLAVA
    "바라클라바": ("HAT", "BALACLAVA", "바라클라바"),
    #TROOPER
    "트루퍼": ("HAT", "TROOPER", "트루퍼"),
    #BUCKET
    "버킷햇": ("HAT", "BUCKET", "버킷햇"),
    #ETC_HAT
    "기타 모자": ("HAT", "ETC_HAT", "기타 모자"),
}

CATEGORIES = {
    "스니커즈": "https://kream.co.kr/search?tab=44&shop_category_id=1&title=%EC%8A%A4%EB%8B%88%EC%BB%A4%EC%A6%88&exclude_filter=shop_category_id",
    "샌들/슬리퍼": "https://kream.co.kr/search?tab=44&shop_category_id=37&title=%EC%83%8C%EB%93%A4/%EC%8A%AC%EB%A6%AC%ED%8D%BC&exclude_filter=shop_category_id",
    "플랫": "https://kream.co.kr/search?tab=44&shop_category_id=70&title=%ED%94%8C%EB%9E%AB&exclude_filter=shop_category_id",
    "로퍼": "https://kream.co.kr/search?tab=44&shop_category_id=69&title=%EB%A1%9C%ED%8D%BC&exclude_filter=shop_category_id",
    "더비/레이스업": "https://kream.co.kr/search?tab=44&shop_category_id=55&title=%EB%8D%94%EB%B9%84/%EB%A0%88%EC%9D%B4%EC%8A%A4%EC%97%85&exclude_filter=shop_category_id",
    "힐/펌프스": "https://kream.co.kr/search?tab=44&shop_category_id=62&title=%ED%9E%90/%ED%8E%8C%ED%94%84%EC%8A%A4&exclude_filter=shop_category_id",
    "부츠": "https://kream.co.kr/search?tab=44&shop_category_id=35&title=%EB%B6%80%EC%B8%A0&exclude_filter=shop_category_id",
    "기타 신발": "https://kream.co.kr/search?tab=44&shop_category_id=71&title=%EA%B8%B0%ED%83%80+%EC%8B%A0%EB%B0%9C&exclude_filter=shop_category_id",
    "바람막이": "https://kream.co.kr/search?tab=49&shop_category_id=22&title=%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4&exclude_filter=shop_category_id",
    "경량 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=150&title=%EA%B2%BD%EB%9F%89+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "플리스 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=162&title=%ED%94%8C%EB%A6%AC%EC%8A%A4+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "숏 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=20&title=%EC%88%8F+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "롱 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=149&title=%EB%A1%B1+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    "경량 패딩": "https://kream.co.kr/search?tab=49&shop_category_id=150&title=%EA%B2%BD%EB%9F%89+%ED%8C%A8%EB%94%A9&exclude_filter=shop_category_id",
    
    "트렌치 코트": "https://kream.co.kr/search?tab=49&shop_category_id=151&title=%ED%8A%B8%EB%A0%8C%EC%B9%98+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "숏 코트": "https://kream.co.kr/search?tab=49&shop_category_id=163&title=%EC%88%8F+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    "롱 코트": "https://kream.co.kr/search?tab=49&shop_category_id=21&title=%EB%A1%B1+%EC%BD%94%ED%8A%B8&exclude_filter=shop_category_id",
    
    "바시티 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=169&title=%EB%B0%94%EC%8B%9C%ED%8B%B0+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "데님 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=166&title=%EB%8D%B0%EB%8B%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "무스탕/퍼": "https://kream.co.kr/search?tab=49&shop_category_id=160&title=%ED%8D%BC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "레더 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=164&title=%EB%A0%88%EB%8D%94+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "블레이저": "https://kream.co.kr/search?tab=49&shop_category_id=156&title=%EB%B8%94%EB%A0%88%EC%9D%B4%EC%A0%80&exclude_filter=shop_category_id",
    "퀼팅 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=157&title=%ED%80%BC%ED%8C%85+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "워크 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=158&title=%EC%9B%8C%ED%81%AC+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "오버 셔츠": "https://kream.co.kr/search?tab=49&shop_category_id=167&title=%EC%98%A4%EB%B2%84%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "후드 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=161&title=%ED%9B%84%EB%93%9C+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "트레이닝 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=165&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "코치 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=168&title=%EC%BD%94%EC%B9%98+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "플리스 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=162&title=%ED%94%8C%EB%A6%AC%EC%8A%A4+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    "기타 자켓": "https://kream.co.kr/search?tab=49&shop_category_id=159&title=%EA%B8%B0%ED%83%80+%EC%9E%90%EC%BC%93&exclude_filter=shop_category_id",
    
    "블루종": "https://kream.co.kr/search?tab=49&shop_category_id=154&title=%EB%B8%94%EB%A3%A8%EC%A2%85&exclude_filter=shop_category_id",
    "바람막이": "https://kream.co.kr/search?tab=49&shop_category_id=22&title=%EB%B0%94%EB%9E%8C%EB%A7%89%EC%9D%B4&exclude_filter=shop_category_id",
    "아노락": "https://kream.co.kr/search?tab=49&shop_category_id=72&title=%EC%95%84%EB%85%B8%EB%9D%BD&exclude_filter=shop_category_id",
    
    "베스트": "https://kream.co.kr/search?tab=49&shop_category_id=153&title=%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "패딩 베스트": "https://kream.co.kr/search?tab=49&shop_category_id=152&title=%ED%8C%A8%EB%94%A9+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    
    "가디건": "https://kream.co.kr/search?tab=50&shop_category_id=75&title=%EA%B0%80%EB%94%94%EA%B1%B4&exclude_filter=shop_category_id",
    
    "후드 집업": "https://kream.co.kr/search?tab=50&shop_category_id=74&title=%ED%9B%84%EB%93%9C+%EC%A7%91%EC%97%85&exclude_filter=shop_category_id",
    
    "기타 아우터": "https://kream.co.kr/search?tab=49&shop_category_id=73&title=%EA%B8%B0%ED%83%80+%EC%95%84%EC%9A%B0%ED%84%B0&exclude_filter=shop_category_id",
    "후드": "https://kream.co.kr/search?tab=50&shop_category_id=23&title=%ED%9B%84%EB%93%9C&exclude_filter=shop_category_id",
    "긴소매 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=26&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "후드 집업": "https://kream.co.kr/search?tab=50&shop_category_id=74&title=%ED%9B%84%EB%93%9C+%EC%A7%91%EC%97%85&exclude_filter=shop_category_id",
    "스웨트셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=24&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=27&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 카라 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=188&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%EC%B9%B4%EB%9D%BC+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "긴소매 카라 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=189&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%EC%B9%B4%EB%9D%BC+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "반소매 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=191&title=%EB%B0%98%EC%86%8C%EB%A7%A4+%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "슬리브리스": "https://kream.co.kr/search?tab=50&shop_category_id=76&title=%EC%8A%AC%EB%A6%AC%EB%B8%8C%EB%A6%AC%EC%8A%A4&exclude_filter=shop_category_id",
    
    "긴소매 티셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=26&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "긴소매 카라 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=189&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%EC%B9%B4%EB%9D%BC+%ED%8B%B0%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    "긴소매 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=190&title=%EA%B8%B4%EC%86%8C%EB%A7%A4+%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    
    "스웨트 셔츠": "https://kream.co.kr/search?tab=50&shop_category_id=24&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%EC%85%94%EC%B8%A0&exclude_filter=shop_category_id",
    
    "후드": "https://kream.co.kr/search?tab=50&shop_category_id=23&title=%ED%9B%84%EB%93%9C&exclude_filter=shop_category_id",
    
    "크루넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=195&title=%ED%81%AC%EB%A3%A8%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "브이넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=193&title=%EB%B8%8C%EC%9D%B4%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "터틀넥 니트": "https://kream.co.kr/search?tab=50&shop_category_id=194&title=%ED%84%B0%ED%8B%80%EB%84%A5+%EB%8B%88%ED%8A%B8&exclude_filter=shop_category_id",
    "니트 베스트": "https://kream.co.kr/search?tab=50&shop_category_id=196&title=%EB%8B%88%ED%8A%B8+%EB%B2%A0%EC%8A%A4%ED%8A%B8&exclude_filter=shop_category_id",
    
    "블라우스": "https://kream.co.kr/search?tab=50&shop_category_id=192&title=%EB%B8%94%EB%9D%BC%EC%9A%B0%EC%8A%A4&exclude_filter=shop_category_id",
    
    "기타 상의": "https://kream.co.kr/search?tab=50&shop_category_id=78&title=%EA%B8%B0%ED%83%80+%EC%83%81%EC%9D%98&exclude_filter=shop_category_id",
    "숏 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=175&title=%EC%88%8F+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "스웨트팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=176&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "트레이닝 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=177&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "데님 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=173&title=%EB%8D%B0%EB%8B%98+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    
    "슬랙스": "https://kream.co.kr/search?tab=51&shop_category_id=179&title=%EC%8A%AC%EB%9E%99%EC%8A%A4&exclude_filter=shop_category_id",
    
    "코튼 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=178&title=%EC%BD%94%ED%8A%BC+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "카고 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=174&title=%EC%B9%B4%EA%B3%A0+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    
    "트레이닝 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=177&title=%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    "스웨트팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=176&title=%EC%8A%A4%EC%9B%A8%ED%8A%B8%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    
    "숏 팬츠": "https://kream.co.kr/search?tab=51&shop_category_id=175&title=%EC%88%8F+%ED%8C%AC%EC%B8%A0&exclude_filter=shop_category_id",
    
    "데님 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "미니 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=79&title=%EB%A0%88%EA%B9%85%EC%8A%A4&exclude_filter=shop_category_id",
    "미디 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=181&title=%EB%AF%B8%EB%94%94+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    "롱 스커트": "https://kream.co.kr/search?tab=51&shop_category_id=182&title=%EB%A1%B1+%EC%8A%A4%EC%BB%A4%ED%8A%B8&exclude_filter=shop_category_id",
    
    "기타 하의": "https://kream.co.kr/search?tab=51&shop_category_id=80&title=%EA%B8%B0%ED%83%80+%ED%95%98%EC%9D%98&exclude_filter=shop_category_id",
    "미니백": "https://kream.co.kr/search?tab=63&shop_category_id=81&title=%EB%AF%B8%EB%8B%88%EB%B0%B1&exclude_filter=shop_category_id",
    "백팩": "https://kream.co.kr/search?tab=63&shop_category_id=82&title=%EB%B0%B1%ED%8C%A9&exclude_filter=shop_category_id",
    
    "크로스백": "https://kream.co.kr/search?tab=63&shop_category_id=83&title=%ED%81%AC%EB%A1%9C%EC%8A%A4%EB%B0%B1&exclude_filter=shop_category_id",
    
    "숄더백": "https://kream.co.kr/search?tab=63&shop_category_id=84&title=%EC%88%84%EB%8D%94%EB%B0%B1&exclude_filter=shop_category_id",
    
    "토트백": "https://kream.co.kr/search?tab=63&shop_category_id=87&title=%ED%86%A0%ED%8A%B8%EB%B0%B1&exclude_filter=shop_category_id",
    "에코백": "https://kream.co.kr/search?tab=63&shop_category_id=88&title=%EC%97%90%EC%BD%94%EB%B0%B1&exclude_filter=shop_category_id",
    
    "미니백": "https://kream.co.kr/search?tab=63&shop_category_id=81&title=%EB%AF%B8%EB%8B%88%EB%B0%B1&exclude_filter=shop_category_id",
    "더플백": "https://kream.co.kr/search?tab=63&shop_category_id=85&title=%EB%8D%94%ED%94%8C%EB%B0%B1&exclude_filter=shop_category_id",
    "클러치": "https://kream.co.kr/search?tab=63&shop_category_id=86&title=%ED%81%B4%EB%9F%AC%EC%B9%98&exclude_filter=shop_category_id",
    "기타 가방": "https://kream.co.kr/search?tab=63&shop_category_id=90&title=%EA%B8%B0%ED%83%80+%EA%B0%80%EB%B0%A9&exclude_filter=shop_category_id",
    "볼캡": "https://kream.co.kr/search?tab=46&shop_category_id=105&title=%EB%B3%BC%EC%BA%A1&exclude_filter=shop_category_id",
    "캠프캡": "https://kream.co.kr/search?tab=46&shop_category_id=201&title=%EC%BA%A0%ED%94%84%EC%BA%A1&exclude_filter=shop_category_id",
    "비니": "https://kream.co.kr/search?tab=46&shop_category_id=103&title=%EB%B9%84%EB%8B%88&exclude_filter=shop_category_id",
    "바라클라바": "https://kream.co.kr/search?tab=46&shop_category_id=203&title=%EB%B0%94%EB%9D%BC%ED%81%B4%EB%9D%BC%EB%B0%94&exclude_filter=shop_category_id",
    "트루퍼": "https://kream.co.kr/search?tab=46&shop_category_id=202&title=%ED%8A%B8%EB%A3%A8%ED%8D%BC%ED%96%87&exclude_filter=shop_category_id",
    "버킷햇": "https://kream.co.kr/search?tab=46&shop_category_id=104&title=%EB%B2%84%ED%82%B7%ED%96%87&exclude_filter=shop_category_id",
    "기타 모자": "https://kream.co.kr/search?tab=46&shop_category_id=106&title=%EA%B8%B0%ED%83%80+%EB%AA%A8%EC%9E%90&exclude_filter=shop_category_id",
}

BASE = "https://kream.co.kr"

# ★ 여기에 본인 쿠키값 넣으세요
MY_COOKIES = [
    {"name": "strategy",   "value": "local",                                "domain": "kream.co.kr", "path": "/"},
    {"name": "webDid",     "value": "dd9550b7-6fb2-44a9-baf2-153249d3f623", "domain": "kream.co.kr", "path": "/"},
    {"name": "ticketExpire", "value": "0",                                  "domain": "kream.co.kr", "path": "/"},
    {"name": "i18n_redirected", "value": "ko",                              "domain": "kream.co.kr", "path": "/"},
    {"name": "ab180ClientId", "value": "5c72f977-c9a4-4344-809d-d815f33e0e3c", "domain": "kream.co.kr", "path": "/"},
]

def only_digits(s):
    return re.sub(r"[^\d]", "", s or "")

def set_cursor(url, cursor_num):
    u = urlparse(url)
    q = parse_qs(u.query)
    q["cursor"] = [str(cursor_num)]
    return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q, doseq=True), u.fragment))

JS_EXTRACT = r"""
() => {
  const results = [];
  const cards = document.querySelectorAll("a.product_card[href*='/products/']");
  for (const card of cards) {
    const href = card.getAttribute("href") || "";

    // 브랜드
    const brandEl = card.querySelector("[data-sdui-id*='product_brand_name'] p");
    const brand = (brandEl?.textContent || "").trim();

    // 상품명
    const allP = card.querySelectorAll("p.text-lookup");
    let name = "";
    for (const p of allP) {
      const t = p.textContent.trim();
      if (t && t !== brand && !t.includes("원") && !t.includes("관심") && !t.includes("리뷰") && !t.includes("거래") && !t.includes("배송") && !t.includes("도착") && !t.includes("%") && !t.includes("적립")) {
        name = t;
        break;
      }
    }

    // 가격 - label-text-container 안의 p태그들 확인
    const labelContainer = card.querySelector(".label-text-container");
    const priceParts = labelContainer ? Array.from(labelContainer.querySelectorAll("p")) : [];
    
    let discountRate = "";
    let salePrice = "";
    let originalPrice = "";

    if (priceParts.length >= 2) {
      // 할인율 + 할인가 둘 다 있는 경우
      const first = priceParts[0].textContent.trim();
      const second = priceParts[1].textContent.trim();
      if (first.includes("%")) {
        discountRate = first.replace(/[^\d]/g, "");
        salePrice = second.replace(/[^\d]/g, "");
      } else {
        salePrice = first.replace(/[^\d]/g, "");
      }
    } else if (priceParts.length === 1) {
      // 할인 없는 경우
      salePrice = priceParts[0].textContent.trim().replace(/[^\d]/g, "");
    }

    // 이미지
    const img = card.querySelector("picture img");
    const imgUrl = (img?.getAttribute("src") || "").trim();

    results.push({ href, brand, name, imgUrl, salePrice, discountRate, originalPrice });
  }
  return results;
}
"""

def wait_for_products(page, timeout=30000):
    try:
        page.wait_for_selector("a.product_card[href*='/products/']", timeout=timeout)
        return True
    except:
        return False

def random_delay(min_sec=REQUEST_DELAY_MIN, max_sec=REQUEST_DELAY_MAX):
    time.sleep(random.uniform(min_sec, max_sec))

def human_like_scroll(page):
    try:
        for _ in range(random.randint(3, 6)):
            page.evaluate(f"window.scrollBy(0, {random.randint(200, 600)})")
            time.sleep(random.uniform(0.5, 1.2))
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(random.uniform(0.8, 1.5))
    except:
        pass

def random_mouse_movement(page):
    try:
        for _ in range(random.randint(2, 4)):
            page.mouse.move(random.randint(100, 1200), random.randint(100, 700))
            time.sleep(random.uniform(0.2, 0.5))
    except:
        pass

def check_for_captcha(page):
    try:
        content = page.content()
        if "일시적인 서비스 장애" in content or "reCAPTCHA" in content or "로봇이 아닙니다" in content:
            print("CAPTCHA 또는 차단 페이지 감지됨!")
            return True
    except:
        pass
    return False

def make_page(context):
    page = context.new_page()
    stealth_sync(page)
    def block(route, request):
        if request.resource_type in ["font", "media"]:
            return route.abort()
        return route.continue_()
    page.route("**/*", block)
    return page

def scrape():
    data_by_category = {
        "SHOES": [], "OUTER": [], "TOP": [],
        "BOTTOM": [], "DRESS": [], "BAG": [], "HAT": []
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

        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            locale='ko-KR',
            timezone_id='Asia/Seoul',
            extra_http_headers={
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
        )

        # ★ 쿠키 주입
        context.add_cookies(MY_COOKIES)

        page = make_page(context)

        print("초기 페이지 방문 중...")
        try:
            page.goto("https://kream.co.kr", wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(5, 8))
            human_like_scroll(page)
        except Exception as e:
            print(f"⚠️ 초기 페이지 로딩 실패: {e}")

        for category_name, base_url in CATEGORIES.items():
            if not base_url:
                continue
            if category_name not in CATEGORY_MAPPING:
                continue

            large_cat, medium_cat, original_cat = CATEGORY_MAPPING[category_name]
            print(f"\n📂 카테고리 시작: {large_cat} > {medium_cat} > {original_cat}")

            category_count = 0
            cursor = 1
            consecutive_failures = 0

            for page_num in range(1, 9999):
                if category_count >= TARGET_PER_CATEGORY:
                    break

                if consecutive_failures >= 3:
                    print(f"연속 실패 {consecutive_failures}번, 60초 휴식...")
                    time.sleep(random.uniform(60, 90))
                    consecutive_failures = 0

                url = set_cursor(base_url, cursor)
                print(f"  ▶ cursor={cursor} 이동 (페이지 {page_num})")

                success = False
                for retry in range(MAX_RETRIES):
                    try:
                        random_delay()
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)

                        if check_for_captcha(page):
                            print(f"  ⚠️ 차단됨! 60초 대기 후 재시도... ({retry+1}/{MAX_RETRIES})")
                            time.sleep(random.uniform(60, 90))
                            continue

                        if not wait_for_products(page, timeout=30000):
                            print(f"  ⚠️ 상품 로드 실패 ({retry+1}/{MAX_RETRIES})")
                            time.sleep(RETRY_DELAY)
                            continue

                        random_mouse_movement(page)
                        time.sleep(random.uniform(PAGE_LOAD_WAIT_MIN, PAGE_LOAD_WAIT_MAX))
                        human_like_scroll(page)
                        success = True
                        consecutive_failures = 0
                        break

                    except Exception as e:
                        print(f" 시도 {retry+1}/{MAX_RETRIES} 실패: {e}")
                        if retry < MAX_RETRIES - 1:
                            wait_time = RETRY_DELAY * (retry + 1)
                            print(f"  ⏳ {wait_time}초 대기 후 재시도...")
                            time.sleep(wait_time)
                        else:
                            consecutive_failures += 1

                if not success:
                    print(f"  💀 모든 재시도 실패. 다음 페이지로...")
                    cursor += 1
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
                    data_by_category[large_cat].append({
                        "대분류": large_cat,
                        "중분류": medium_cat,
                        "카테고리": original_cat,
                        "상품명": it.get("name", "") or "",
                        "브랜드": it.get("brand", "") or "",
                        "정가": it.get("originalPrice", "") or "",
                        "판매가": it.get("salePrice", "") or "",
                        "할인율(%)": it.get("discountRate", "") or "",
                        "상품 URL": full_url,
                        "이미지 URL": it.get("imgUrl", "") or "",
                    })
                    if category_count >= TARGET_PER_CATEGORY:
                        break

                print(f"    [{original_cat}] 누적: {category_count}개 (+{added})")

                if added == 0:
                    print(f"cursor={cursor}에서 추가 0개 → 종료")
                    break

                cursor += 1

                if page_num % 5 == 0:
                    rest_time = random.uniform(30, 45)
                    print(f" 5페이지 완료, {rest_time:.1f}초 휴식...")
                    time.sleep(rest_time)

            print(f"✅ END: {original_cat} (수집 {category_count}개)")
            time.sleep(random.uniform(15, 25))

        browser.close()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fieldnames = ["대분류", "중분류", "카테고리", "상품명", "브랜드",
                  "정가", "판매가", "할인율(%)", "상품 URL", "이미지 URL"]

    total_count = 0
    for large_cat, rows in data_by_category.items():
        if not rows:
            continue
        output_file = os.path.join(OUTPUT_DIR, f"{large_cat}.csv")
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(rows)
        total_count += len(rows)
        print(f"\n{large_cat} CSV 저장 완료: {output_file} ({len(rows)}개)")

    print(f"\n전체 CSV 저장 완료: {OUTPUT_DIR}/ (총 {total_count}개)")


if __name__ == "__main__":
    scrape()