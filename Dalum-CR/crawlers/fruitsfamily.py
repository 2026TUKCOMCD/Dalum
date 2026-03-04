from playwright.sync_api import sync_playwright
import csv
import time
import os

# ===============================
# 경로 설정
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "fruitsfamily")


CATEGORIES = {
    "중고_상의": "https://fruitsfamily.com/discover/product/상의",
    "중고_아우터": "https://fruitsfamily.com/discover/product/아우터",
    "중고_하의": "https://fruitsfamily.com/discover/product/하의",
    "중고_신발": "https://fruitsfamily.com/discover/product/신발",
    "중고_가방": "https://fruitsfamily.com/discover/product/가방",
    "중고_모자": "https://fruitsfamily.com/discover/product/모자",
    "중고_치마": "https://fruitsfamily.com/discover/product/치마",
    "중고_원피스": "https://fruitsfamily.com/discover/product/원피스"
}

# ===============================
# 공통 대/중분류 매핑 (※ 여기만 나중에 채우면 됨)
# ===============================
CATEGORY_MAP = {
    "중고_상의": {"대분류": "TOP", "중분류": "USED_TOP"},
    "중고_아우터": {"대분류": "OUTER", "중분류": "USED_OUTER"},
    "중고_하의": {"대분류": "BOTTOM", "중분류": "USED_BOTTOM"},
    "중고_신발": {"대분류": "SHOES", "중분류": "USED_SHOES"},
    "중고_가방": {"대분류": "BAG", "중분류": "USED_BAG"},
    "중고_모자": {"대분류": "HAT", "중분류": "USED_HAT"},
    "중고_치마": {"대분류": "BOTTOM", "중분류": "USED_SKIRT"},
    "중고_원피스": {"대분류": "DRESS", "중분류": "USED_ONE_PIECE"}
}

# ===============================
# 정가 계산
# ===============================
def calculate_original_price(sale_price, discount_rate):
    if discount_rate <= 0:
        return "-"
    try:
        original = sale_price * 100 / (100 - discount_rate)
        return int(round(original, -1))
    except:
        return "-"

# ===============================
# JS: 화면에 렌더된 상품 스냅샷
# ===============================
JS_EXTRACT = """
() => {
  const results = [];
  const items = document.querySelectorAll("div.ProductsListItem");

  for (const item of items) {
    const link = item.querySelector("a.ProductPreview");
    if (!link) continue;

    const href = link.href;

    const img = link.querySelector("img.ProductPreview-image");
    const imgUrl = img?.src || "";
    const name = img?.alt || "";

    const brand =
      item.querySelector(".ProductsListItem-brand")?.innerText.trim() || "";

    const priceText =
      item.querySelector(".ProductsListItem-price")
        ?.innerText.replace(/[^0-9]/g, "") || "";

    const discountText =
      item.querySelector(".ProductsListItem-discount-rate")
        ?.innerText.replace(/[^0-9]/g, "") || "";

    results.push({
      brand,
      name,
      href,
      imgUrl,
      price: priceText,
      discount: discountText
    });
  }
  return results;
}
"""

# ===============================
# Infinite Scroll 대응
# ===============================
def scroll_to_bottom(page):
    page.evaluate("""
    () => {
        const items = document.querySelectorAll("div.ProductsListItem");
        if (items.length > 0) {
            items[items.length - 1].scrollIntoView({ behavior: "smooth" });
        }
    }
    """)

# ===============================
# 메인 크롤러
# ===============================
def scrape():
    rows = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=30)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for category_name, url in CATEGORIES.items():
            print(f"\n📂 {category_name}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("div.ProductsListItem", timeout=30000)
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

                    sale_price = int(it["price"]) if it["price"] else 0
                    discount_rate = int(it["discount"]) if it["discount"] else 0

                    original_price = (
                        calculate_original_price(sale_price, discount_rate)
                        if discount_rate > 0
                        else "-"
                    )

                    cat = CATEGORY_MAP[category_name]

                    rows.append({
                        "대분류": cat["대분류"],
                        "중분류": cat["중분류"],
                        "카테고리": category_name,
                        "브랜드": it["brand"],
                        "상품명": it["name"],
                        "정가": original_price,
                        "판매가": sale_price,
                        "할인율(%)": discount_rate if discount_rate > 0 else "-",
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

    # 대분류별 CSV 저장 (헤더 ❌)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grouped = {}
    for r in rows:
        grouped.setdefault(r["대분류"], []).append(r)

    for major, items in grouped.items():
        path = os.path.join(OUTPUT_DIR, f"{major}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)

        print(f"✅ {major}.csv 저장 ({len(items)}개)")

# ===============================
if __name__ == "__main__":
    scrape()
