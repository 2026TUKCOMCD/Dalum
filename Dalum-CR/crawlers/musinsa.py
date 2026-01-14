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
    #OUTER
    "숏패딩": "https://www.musinsa.com/category/002012",
    "경량패딩": "https://www.musinsa.com/category/002027",
    "롱패딩": "https://www.musinsa.com/category/002013",
    "무스탕/퍼": "https://www.musinsa.com/category/002025",
    "레더자켓": "https://www.musinsa.com/category/002002",
    "야상": "https://www.musinsa.com/category/002014",
    "싱글코트": "https://www.musinsa.com/category/002007",
    "더블코트": "https://www.musinsa.com/category/002024",
    "후드집업": "https://www.musinsa.com/category/002022",
    "베스트": "https://www.musinsa.com/category/002021",
    #TOP
    "맨투맨/스웨트": "https://www.musinsa.com/category/001005",
    "후드": "https://www.musinsa.com/category/001004?gf=A",
    "셔츠/블라우스": "https://www.musinsa.com/category/001002",
    "니트/스웨터": "https://www.musinsa.com/category/001006",
    "반소매티셔츠": "https://www.musinsa.com/category/001001",
    "김소매티셔츠": "https://www.musinsa.com/category/001010",
    #BOTTOM
    "데님팬츠": "https://www.musinsa.com/category/003002",
    "슬랙스/슈트팬츠": "https://www.musinsa.com/category/003008",
    "트레이닝/조거팬츠": "https://www.musinsa.com/category/003004",
    "숏팬츠": "https://www.musinsa.com/category/003009",
    "기타팬츠": "https://www.musinsa.com/category/003006",
    #SHOES
    "스니커즈": "https://www.musinsa.com/category/103004",
    "부츠/워커": "https://www.musinsa.com/category/103002",
    "샌들/슬리퍼": "https://www.musinsa.com/category/103003",
    "기타신발": "https://www.musinsa.com/category/103005",
    #BAG
    "메신저/크로스백": "https://www.musinsa.com/category/004002",
    "백팩": "https://www.musinsa.com/category/004001",
    "토트백": "https://www.musinsa.com/category/004015",
    #HAT
    "캡모자": "https://www.musinsa.com/category/101001001",
    "비니": "https://www.musinsa.com/category/101001005",
    "바라클라바": "https://www.musinsa.com/category/101001008",
    "트루퍼": "https://www.musinsa.com/category/101001006",
    "페도라": "https://www.musinsa.com/category/101001003",
    "베레모": "https://www.musinsa.com/category/101001002",
    "기타모자": "https://www.musinsa.com/category/101001007"
}

# ===============================
# 무신사 → 공통 대/중분류 매핑
# ===============================
CATEGORY_MAP = {
    #OUTER
    "숏패딩": {"대분류": "OUTER","중분류": "PADDING"},
    "경량패딩": {"대분류": "OUTER","중분류": "PADDING"},
    "롱패딩": {"대분류": "OUTER","중분류": "PADDING"},
    "무스탕/퍼": {"대분류": "OUTER","중분류": "JACKET"},
    "레더자켓": {"대분류": "OUTER","중분류": "JACKET"},
    "야상": {"대분류": "OUTER","중분류": "JACKET"},
    "싱글코트": {"대분류": "OUTER","중분류": "COAT"},
    "더블코트": {"대분류": "OUTER","중분류": "COAT"},
    "후드집업": {"대분류": "OUTER","중분류": "HOODED_ZIP_UP"},
    "베스트": {"대분류": "OUTER","중분류": "VEST"},
    #TOP
    "맨투맨/스웨트": {"대분류": "TOP","중분류": "SWEATSHIRT"},
    "후드": {"대분류": "TOP","중분류": "HOODIE"},
    "셔츠/블라우스": {"대분류": "TOP","중분류": "SHIRT_BLOUSE"},
    "니트/스웨터": {"대분류": "TOP","중분류": "KNIT"},
    "반소매티셔츠": {"대분류": "TOP","중분류": "TSHIRT"},
    "김소매티셔츠": {"대분류": "TOP","중분류": "LSHIRT"},
    #BOTTOM
    "데님팬츠": {"대분류": "BOTTOM","중분류": "DENIM"},
    "슬랙스/슈트팬츠": {"대분류": "BOTTOM","중분류": "SLACKS"},
    "트레이닝/조거팬츠": {"대분류": "BOTTOM","중분류": "TRAINING_PANTS"},
    "숏팬츠": {"대분류": "BOTTOM","중분류": "SHORTS"},
    "기타팬츠": {"대분류": "BOTTOM","중분류": "-"},
    #SHOES
    "스니커즈": {"대분류": "SHOES","중분류": "SNEAKERS"},
    "부츠/워커": {"대분류": "SHOES","중분류": "BOOTS"},
    "샌들/슬리퍼": {"대분류": "SHOES","중분류": "SANDAL_SLIPPER"},
    "기타신발": {"대분류": "SHOES","중분류": "ETC_SHOES"},
    #BAG
    "메신저/크로스백": {"대분류": "BAG","중분류": "CROSSBODY"},
    "백팩": {"대분류": "BAG","중분류": "BACKPACK"},
    "토트백": {"대분류": "BAG","중분류": "TOTE"},
    #HAT
    "캡모자": {"대분류": "HAT","중분류": "CAP"},
    "비니": {"대분류": "HAT","중분류": "BEANIE"},
    "바라클라바": {"대분류": "HAT","중분류": "BALACLAVA"},
    "트루퍼": {"대분류": "HAT","중분류": "TROOPER"},
    "페도라": {"대분류": "HAT","중분류": "FEDORA"},
    "베레모": {"대분류": "HAT","중분류": "BERET"},
    "기타모자": {"대분류": "HAT","중분류": "ETC_HAT"}
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