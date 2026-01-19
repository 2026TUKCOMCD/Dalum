from playwright.sync_api import sync_playwright
import csv
import time
import re
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# ===============================
# 출력 설정
# ===============================
OUTPUT_DIR = "/Users/kang/Desktop/Dalum/Dalum-CR/output/29cm"
MAX_PAGES_PER_CATEGORY = 9999
PAGE_PAUSE_SEC = 0.25
EMPTY_PAGES_STOP = 2

# ===============================
# 카테고리 구조
# ===============================
CATEGORIES = {
    # ---------------- OUTER ----------------
    ("OUTER", "PADDING", "야상"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102122&page=1",
    ("OUTER", "PADDING", "경량패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102105&page=1",
    ("OUTER", "PADDING", "숏패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102104&page=1",
    ("OUTER", "PADDING", "롱패딩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102103&page=1",
    ("OUTER", "PADDING", "베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102106&page=1",
    
    ("OUTER", "COAT", "트렌치/맥코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102102&page=1",
    ("OUTER", "COAT", "숏코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102117&page=1",
    ("OUTER", "COAT", "하프코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102118&page=1",
    ("OUTER", "COAT", "롱코트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102119&page=1",
    
    ("OUTER", "JACKET", "블루종"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102123&page=1",
    ("OUTER", "JACKET", "바시티"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102124&page=1",
    ("OUTER", "JACKET", "데님 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102125&page=1",
    ("OUTER", "JACKET", "퍼 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102126&page=1",
    ("OUTER", "JACKET", "트레이닝 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102127&page=1",
    ("OUTER", "JACKET", "점퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102128&page=1",
    ("OUTER", "JACKET", "바람막이"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102129&page=1",
    ("OUTER", "JACKET", "아노락"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102130&page=1",
    ("OUTER", "JACKET", "나일론/코치 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102112&page=1",
    ("OUTER", "JACKET", "레더 재킷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102111&page=1",
    ("OUTER", "JACKET", "블레이저"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102110&page=1",
    ("OUTER", "JACKET", "무스탕"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102116&page=1",
    
    ("OUTER", "VEST", "베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102106&page=1",
    
    ("OUTER", "CARDIGAN", "카디건"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110104&page=1",
    
    ("OUTER", "HOODED_ZIP_UP", "후드 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102109&page=1",
    ("OUTER", "HOODED_ZIP_UP", "집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103109&page=1",
    ("OUTER", "HOODED_ZIP_UP", "니트 집업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110106&page=1",
    
    ("OUTER", "ETC_OUTER", "기타 아우터"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102113&page=1",

    # ---------------- TOP ----------------
    ("TOP", "TSHIRT", "반소매 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103101&page=1",
    ("TOP", "TSHIRT", "긴소매 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103102&page=1",
    ("TOP", "TSHIRT", "피케/카라 티셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103104&page=1",
    ("TOP", "TSHIRT", "슬리브리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103103&page=1",
    
    ("TOP", "SHIRT_BLOUSE", "반소매 셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103105&page=1",
    ("TOP", "SHIRT_BLOUSE", "긴소매 셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103106&page=1",
    
    ("TOP", "SWEATSHIRT", "스웨트셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103107&page=1",
    
    ("TOP", "HOODIE", "후디"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272103100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272103108&page=1",
    ("TOP", "HOODIE", "니트 후드"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110108&page=1",
    
    ("TOP", "KNIT", "크루넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110101&page=1",
    ("TOP", "KNIT", "브이넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110102&page=1",
    ("TOP", "KNIT", "터틀넥"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110103&page=1",
    ("TOP", "KNIT", "폴로셔츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110107&page=1",
    ("TOP", "KNIT", "니트 베스트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110105&page=1",
    ("TOP", "FLEECE", "플리스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272102100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272102114&page=1",
    ("TOP", "ETC_TOP", "기타 니트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272110100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272110109&page=1",
    
    # ---------------- BOTTOM ----------------
    ("BOTTOM", "DENIM", "데님 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104104&page=1",
    
    ("BOTTOM", "SLACKS", "슬랙스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104106&page=1",
    
    ("BOTTOM", "COTTON_PANTS", "코튼 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104105&page=1",
    ("BOTTOM", "COTTON_PANTS", "슬림 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104103&page=1",
    ("BOTTOM", "COTTON_PANTS", "스트레이트 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104101&page=1",
    ("BOTTOM", "COTTON_PANTS", "와이드 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104102&page=1",
    ("BOTTOM", "COTTON_PANTS", "부츠컷"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104109&page=1",
    
    ("BOTTOM", "TRAINING_PANTS", "트레이닝 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104107&page=1",
    
    ("BOTTOM", "SHORTS", "쇼트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104108&page=1",
    
    ("BOTTOM", "LEGGINGS", "레깅스"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104110&page=1",
    
    ("BOTTOM", "ETC_BOTTOM", "기타 팬츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272104100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272104111&page=1",

    # ---------------- DRESS ----------------
    ("DRESS", "SETUP", "수트 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112101&page=1",
    ("DRESS", "SETUP", "기타 상하의 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112104&page=1",
    ("DRESS", "SETUP", "스웻/트레이닝 셋업"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272112100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272112103&page=1",
    ("DRESS", "SETUP", "홈웨어 세트"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113103&page=1",
    ("DRESS", "SETUP", "로브"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=272100100&categoryMediumCode=272113100&sort=RECOMMENDED&defaultSort=RECOMMENDED&categorySmallCode=272113104&page=1",

    # ---------------- BAG ----------------
    ("BAG", "BACKPACK", "백팩"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273104100",
    
    ("BAG", "CROSSBODY", "크로스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273101100",
    ("BAG", "CROSSBODY", "웨이스트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273102100",
    
    ("BAG", "SHOULDER", "숄더백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273105100",
    
    ("BAG", "TOTE", "토트백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273103100",
    ("BAG", "TOTE", "에코/캔버스백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273107100",
    
    ("BAG", "CLUTCH", "클러치"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273115100",
    
    ("BAG", "ETC_BAG", "보스턴백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273119100",
    ("BAG", "ETC_BAG", "캐리어/여행가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273118100",
    ("BAG", "ETC_BAG", "랩탑백"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273106100",
    ("BAG", "ETC_BAG", "기타 가방"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=273100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=273110100",

    # ---------------- SHOES ----------------
    ("SHOES", "SNEAKERS", "스니커즈"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274101100",
    
    ("SHOES", "BOOTS", "부츠"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274104100",
    
    ("SHOES", "LOAFER", "로퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274102100",
    ("SHOES", "LOAFER", "구두"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274103100",
    
    ("SHOES", "SANDAL_SLIPPER", "샌들"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274105100",
    ("SHOES", "SANDAL_SLIPPER", "슬리퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274110100",
    
    ("SHOES", "SPORTS_SHOES", "기능화"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=274100100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categoryMediumCode=274115100",

    # ---------------- HAT ----------------
    ("HAT", "CAP", "볼캡"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101103",
    ("HAT", "CAP", "버킷햇"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101101",
    ("HAT", "CAP", "선캡/바이저"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101109",
    
    ("HAT", "BEANIE", "비니"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101104",
    ("HAT", "BEANIE", "워치캡"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101110",
    
    ("HAT", "BALACLAVA", "바라클라바"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101106",
    
    ("HAT", "TROOPER", "트루퍼"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101107",
    
    ("HAT", "FEDORA", "페도라"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101105",
    
    ("HAT", "BERET", "베레모"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101102",
    
    ("HAT", "ETC_HAT", "기타 모자"): "https://www.29cm.co.kr/store/category/list?categoryLargeCode=275100100&categoryMediumCode=275101100&sort=RECOMMENDED&defaultSort=RECOMMENDED&page=1&categorySmallCode=275101108",
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
# 개선된 가격 추출 JavaScript
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

    // ⭐ 개선: 가격 박스를 더 정확하게 찾기
    let price = "", discount = "";
    
    // 방법 1: text-primary 또는 text-xxl-bold 클래스가 있는 div 찾기 (가격 박스의 특징)
    let priceBox = null;
    const priceBoxCandidates = box?.querySelectorAll("div.items-center") || [];
    
    for (const candidate of priceBoxCandidates) {
      // p 태그가 있고, 그 안에 숫자나 %가 있는 것만 가격 박스로 인정
      const ps = candidate.querySelectorAll("p");
      if (ps.length > 0) {
        const hasPrice = Array.from(ps).some(p => {
          const text = (p.textContent || "").trim();
          return /\d/.test(text) || text.includes("%");
        });
        
        if (hasPrice) {
          priceBox = candidate;
          break;
        }
      }
    }
    
    if (priceBox) {
      const ps = Array.from(priceBox.querySelectorAll("p"));
      const texts = ps.map(p => (p.textContent || "").trim()).filter(Boolean);
      
      // 할인율 찾기
      const discountItem = texts.find(t => t.includes("%"));
      if (discountItem) {
        discount = discountItem;
      }
      
      // 가격 찾기
      const priceItem = texts.find(t => !t.includes("%") && /\d/.test(t));
      if (priceItem) {
        price = priceItem;
      }
    }
    
    // 방법 2: 여전히 못 찾았으면 box 전체에서 "숫자+원" 패턴 찾기
    if (!price && box) {
      const allText = box.innerText || "";
      const priceMatch = allText.match(/(\d{1,3}(?:,\d{3})*)\s*원/);
      if (priceMatch) {
        price = priceMatch[1];
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    data_by_category = {
        "OUTER": [],
        "TOP": [],
        "BOTTOM": [],
        "DRESS": [],
        "BAG": [],
        "SHOES": [],
        "HAT": []
    }
    
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

        for (main_cat, sub_cat, original_cat), base_url in CATEGORIES.items():
            if not base_url.strip():
                print(f"⏭ URL 없음 → 스킵: {main_cat}/{sub_cat}/{original_cat}")
                continue

            print(f"\n📂 START: {main_cat} / {sub_cat} / {original_cat}")
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

                    row = {
                        "대분류": main_cat,
                        "중분류": sub_cat,
                        "카테고리": original_cat,
                        "상품명": it.get("name", "") or "",
                        "브랜드": it.get("brand", "") or "",
                        "정가": original,
                        "판매가": sell,
                        "할인율(%)": rate,
                        "상품 URL": href,
                        "이미지 URL": it.get("imgUrl", "") or "",
                    }
                    
                    data_by_category[main_cat].append(row)

                if added == 0:
                    empty_pages += 1
                    if empty_pages >= EMPTY_PAGES_STOP:
                        break
                else:
                    empty_pages = 0

            print(f"✅ END: {main_cat}/{sub_cat}/{original_cat}")

        browser.close()

    # CSV 저장
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
            writer.writerows(rows)
        
        total_count += len(rows)
        print(f"\n✅ {large_cat} CSV 저장 완료: {output_file} ({len(rows):,}개)")

    print(f"\n✅ 전체 CSV 저장 완료: {OUTPUT_DIR}/ (총 {total_count:,}개)")


if __name__ == "__main__":
    scrape()