from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import csv
import time
import os

# ===============================
# 설정
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "musinsa")

CATEGORIES = {
    # [OUTER 카테고리]
    #PADDING
    "숏 패딩": "https://www.musinsa.com/category/002012",
    "롱 패딩": "https://www.musinsa.com/category/002013",
    "경량 패딩": "https://www.musinsa.com/category/002027",
    #COAT
    "싱글 코트": "https://www.musinsa.com/category/002007",
    "더블 코트": "https://www.musinsa.com/category/002024",
    #JACKET
    "데님 자켓" : "https://www.musinsa.com/category/002017",
    "무스탕/퍼": "https://www.musinsa.com/category/002025",
    "레더 자켓": "https://www.musinsa.com/category/002002",
    "블레이저": "https://www.musinsa.com/category/002003",
    "트레이닝 자켓": "https://www.musinsa.com/category/002018",
    "코치 자켓": "https://www.musinsa.com/category/002006",
    "플리스 자켓": "https://www.musinsa.com/category/002023",
    #JUMPER 
    "블루종": "https://www.musinsa.com/category/002001",
    "야상": "https://www.musinsa.com/category/002014",
    "아노락": "https://www.musinsa.com/category/002019",
    #VEST
    "베스트": "https://www.musinsa.com/category/002021",
    #CARDIGAN
    "가디건": "https://www.musinsa.com/category/002020",
    #ZIP_UP
    "후드 집업": "https://www.musinsa.com/category/002022",
    #ETC_OUTER
    "기타 아우터": "https://www.musinsa.com/category/002015",
    
    
    #[TOP 카테고리]
    #TSHIRT
    "티셔츠": "https://www.musinsa.com/category/001001",
    #LSHIRT
    "긴소매 티셔츠": "https://www.musinsa.com/category/001010",
    "긴소매 셔츠": "https://www.musinsa.com/category/001002",
    #SWEATSHIRT
    "스웨트 셔츠": "https://www.musinsa.com/category/001005",
    #HOODIE
    "후드": "https://www.musinsa.com/category/001004?gf=A",
    #KNIT
    "니트": "https://www.musinsa.com/category/001006",
    
    # [BOTTOM 카테고리]
    #DENIM
    "데님팬츠": "https://www.musinsa.com/category/003002",
    #SLACKS
    "슬랙스": "https://www.musinsa.com/category/003008",
    #PANTS
    "코튼 팬츠": "https://www.musinsa.com/category/003007",
    "트레이닝 팬츠": "https://www.musinsa.com/category/003004",
    #SHORT_PANTS
    "숏팬츠": "https://www.musinsa.com/category/003009",
    #ETC_BOTTOM
    "기타팬츠": "https://www.musinsa.com/category/003006",
    
    #[DRESS 카테고리]
    #ONE_PIECE
    "미디 원피스": "https://www.musinsa.com/category/100002",
    "맥시 원피스": "https://www.musinsa.com/category/100003",
    "미니 원피스": "https://www.musinsa.com/category/100001",
    
    #[BAG 카테고리]
    #BACKPACK
    "백팩": "https://www.musinsa.com/category/004001",
    #CROSSBODY
    "크로스백": "https://www.musinsa.com/category/004002",
    #WAIST
    "웨이스트백": "https://www.musinsa.com/category/004007",
    #SHOULDER
    "숄더백": "https://www.musinsa.com/category/004003",
    #TOTE
    "토트백": "https://www.musinsa.com/category/004015",
    "에코백": "https://www.musinsa.com/category/004014",
    #ETC_BAG
    "보스턴백": "https://www.musinsa.com/category/004006",
    
    #[SHOES 카테고리]
    #SNEAKERS
    "스니커즈": "https://www.musinsa.com/category/103004004",
    "로우탑": "https://www.musinsa.com/category/103004001",
    "뮬": "https://www.musinsa.com/category/103004002",
    "슬립온": "https://www.musinsa.com/category/103004003",
    "운동화": "https://www.musinsa.com/category/103004005",
    #BOOTS
    "워커 부츠": "https://www.musinsa.com/category/103002007",
    "숏 부츠": "https://www.musinsa.com/category/103002001",
    "미들 부츠": "https://www.musinsa.com/category/103002002",
    "레인 부츠": "https://www.musinsa.com/category/103002005",
    #LOAFER
    "구두": "https://www.musinsa.com/category/103001",
    #SANDAL_SLIPPER
    "샌들/슬리퍼": "https://www.musinsa.com/category/103003",
    
    #[HAT 카테고리]
    #CAP
    "볼캡": "https://www.musinsa.com/category/101001001",
    #BEANIE
    "비니": "https://www.musinsa.com/category/101001005",
    #BALACLAVA
    "바라클라바": "https://www.musinsa.com/category/101001008",
    #TROOPER
    "트루퍼": "https://www.musinsa.com/category/101001006",
    #FEDORA
    "페도라": "https://www.musinsa.com/category/101001003",
    #BERET
    "베레모": "https://www.musinsa.com/category/101001002",
    #ETC_HAT
    "기타 모자": "https://www.musinsa.com/category/101001007"
}

# ===============================
# 무신사 → 공통 대/중분류 매핑
# ===============================
CATEGORY_MAP = {
    #[OUTER 카테고리]
    #OUTER
    "숏 패딩": {"대분류": "OUTER","중분류": "PADDING"},
    "경량 패딩": {"대분류": "OUTER","중분류": "PADDING"},
    "롱 패딩": {"대분류": "OUTER","중분류": "PADDING"},

    "데님 자켓": {"대분류": "OUTER","중분류": "JACKET"},
    "무스탕/퍼": {"대분류": "OUTER","중분류": "JACKET"},
    "레더 자켓": {"대분류": "OUTER","중분류": "JACKET"},
    "블레이저": {"대분류": "OUTER","중분류": "JACKET"},
    "트레이닝 자켓": {"대분류": "OUTER","중분류": "JACKET"},
    "코치 자켓": {"대분류": "OUTER","중분류": "JACKET"},
    "플리스 자켓": {"대분류": "OUTER","중분류": "JACKET"},

    "블루종": {"대분류": "OUTER","중분류": "JUMPER"},
    "야상": {"대분류": "OUTER","중분류": "JUMPER"},
    "아노락": {"대분류": "OUTER","중분류": "JUMPER"},

    "싱글 코트": {"대분류": "OUTER","중분류": "COAT"},
    "더블 코트": {"대분류": "OUTER","중분류": "COAT"},

    "베스트": {"대분류": "OUTER","중분류": "VEST"},

    "가디건": {"대분류": "OUTER","중분류": "CARDIGAN"},

    "후드 집업": {"대분류": "OUTER","중분류": "ZIP_UP"},

    "기타 아우터": {"대분류": "OUTER","중분류": "ETC_OUTER"},

    #TOP
    "티셔츠": {"대분류": "TOP","중분류": "TSHIRT"},
    "긴소매 티셔츠": {"대분류": "TOP","중분류": "LSHIRT"},
    "긴소매 셔츠": {"대분류": "TOP","중분류": "LSHIRT"},
    "스웨트 셔츠": {"대분류": "TOP","중분류": "SWEATSHIRT"},
    "후드": {"대분류": "TOP","중분류": "HOODIE"},
    "니트": {"대분류": "TOP","중분류": "KNIT"},

    #BOTTOM
    "데님 팬츠": {"대분류": "BOTTOM","중분류": "DENIM"},
    "슬랙스": {"대분류": "BOTTOM","중분류": "SLACKS"},
    "코튼 팬츠": {"대분류": "BOTTOM","중분류": "PANTS"},
    "트레이닝 팬츠": {"대분류": "BOTTOM","중분류": "PANTS"},
    "숏 팬츠": {"대분류": "BOTTOM","중분류": "SHORT_PANTS"},
    "기타 팬츠": {"대분류": "BOTTOM","중분류": "ETC_BOTTOM"},
    #DRESS
    "미디 원피스": {"대분류": "DRESS","중분류": "ONE_PIECE"},
    "맥시 원피스": {"대분류": "DRESS","중분류": "ONE_PIECE"},
    "미니 원피스": {"대분류": "DRESS","중분류": "ONE_PIECE"},
    #BAG
    "백팩": {"대분류": "BAG","중분류": "BACKPACK"},
    "크로스백": {"대분류": "BAG","중분류": "CROSSBODY"},
    "웨이스트백": {"대분류": "BAG","중분류": "WAIST"},
    "숄더백": {"대분류": "BAG","중분류": "SHOULDER"},
    "토트백": {"대분류": "BAG","중분류": "TOTE"},
    "에코백": {"대분류": "BAG","중분류": "TOTE"},
    "보스턴백": {"대분류": "BAG","중분류": "ETC_BAG"},
    #SHOES
    "스니커즈": {"대분류": "SHOES","중분류": "SNEAKERS"},
    "로우탑": {"대분류": "SHOES","중분류": "SNEAKERS"},
    "뮬": {"대분류": "SHOES","중분류": "SNEAKERS"},
    "슬립온": {"대분류": "SHOES","중분류": "SNEAKERS"},
    "운동화": {"대분류": "SHOES","중분류": "SNEAKERS"},

    "워커 부츠": {"대분류": "SHOES","중분류": "BOOTS"},
    "숏 부츠": {"대분류": "SHOES","중분류": "BOOTS"},
    "미들 부츠": {"대분류": "SHOES","중분류": "BOOTS"},
    "레인 부츠": {"대분류": "SHOES","중분류": "BOOTS"},

    "구두": {"대분류": "SHOES","중분류": "LOAFER"},

    "샌들/슬리퍼": {"대분류": "SHOES","중분류": "SANDAL_SLIPPER"},
    
    #HAT
    "캡모자": {"대분류": "HAT","중분류": "CAP"},
    "비니": {"대분류": "HAT","중분류": "BEANIE"},
    "바라클라바": {"대분류": "HAT","중분류": "BALACLAVA"},
    "트루퍼": {"대분류": "HAT","중분류": "TROOPER"},
    "페도라": {"대분류": "HAT","중분류": "FEDORA"},
    "베레모": {"대분류": "HAT","중분류": "BERET"},
    "기타 모자": {"대분류": "HAT","중분류": "ETC_HAT"}
}

# ===============================
# JS: 화면에 렌더된 상품 스냅샷
# ===============================
JS_EXTRACT = """
() => {
  const results = [];
  const anchors = document.querySelectorAll(
    "div[data-testid='virtuoso-item-list'] div[data-index] a.gtm-select-item"
  );

  for (const a of anchors) {
    const href = a.href || "";
    if (!href.includes("/products/")) continue;

    const brand = a.getAttribute("data-brand-id") || "";
    const price = a.getAttribute("data-price") || "";
    const original = a.getAttribute("data-original-price") || "";
    const discount = a.getAttribute("data-discount-rate") || "";

    const img = a.querySelector("img");
    const name = img?.getAttribute("alt") || "";
    const imgUrl = img?.getAttribute("src") || "";

    results.push({ brand, name, href, imgUrl, price, original, discount });
  }
  return results;
}
"""
# ===============================
def scroll_to_bottom(page):
    page.evaluate("""
    () => {
      const items = document.querySelectorAll("div[data-index]");
      if (items.length > 0) {
        items[items.length - 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
    """)

# ===============================
def scrape():
    rows = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=30)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for category_name, url in CATEGORIES.items():
            print(f"\n📂 {category_name}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            try:
                page.wait_for_selector(
                    "div[data-testid='virtuoso-item-list']", timeout=30000
                )
            except PlaywrightTimeoutError:
                print(f"⚠ [{category_name}] 상품 리스트 로딩 실패 → skip")
                continue

            time.sleep(1)

            stagnant = 0

            while True:
                snapshot = page.evaluate(JS_EXTRACT)
                added = 0

                for it in snapshot:
                    if it["href"] in seen:
                        continue

                    seen.add(it["href"])
                    added += 1

                    cat = CATEGORY_MAP[category_name]

                    rows.append({
                        "대분류": cat["대분류"],
                        "중분류": cat["중분류"],
                        "카테고리": category_name,
                        "브랜드": it["brand"],
                        "상품명": it["name"],
                        "정가": it["original"],
                        "판매가": it["price"],
                        "할인율(%)": it["discount"],
                        "상품 URL": it["href"],
                        "이미지 URL": it["imgUrl"],
                    })

                print(f"  → 신규 {added}개")

                stagnant = stagnant + 1 if added == 0 else 0
                if stagnant >= 6:
                    print(f"  ⚠ {category_name} 크롤링 종료")
                    break

                scroll_to_bottom(page)
                time.sleep(0.8)

        browser.close()

    # ===============================
    # 대분류별 CSV 저장
    # ===============================
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grouped = {}
    for r in rows:
        grouped.setdefault(r["대분류"], []).append(r)

    for major, items in grouped.items():
        path = os.path.join(OUTPUT_DIR, f"{major}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writerows(items)  # 헤더 없음

        print(f"✅ {major}.csv 저장 ({len(items)}개)")

# ===============================
if __name__ == "__main__":
    scrape()