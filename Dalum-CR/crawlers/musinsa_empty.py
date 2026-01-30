from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
import csv
import time
import os

# ===============================
# 경로 설정
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "musinsa-empty")

MAX_PAGES_PER_CATEGORY = 200
NO_NEW_PAGES_LIMIT = 3
REPEAT_PAGE_LIMIT = 2
ROUND_UNIT_WON = 10
BASE_URL = "https://empty.seoul.kr"

CATEGORIES = {
    #OUTER
    "숏 패딩": "https://empty.seoul.kr/product/list.html?cate_no=109",
    "코트": "https://empty.seoul.kr/product/list.html?cate_no=93",
    "레더 자켓": "https://empty.seoul.kr/product/list.html?cate_no=90",
    "무스탕/퍼": "https://empty.seoul.kr/product/list.html?cate_no=148",
    #TOP
    "티셔츠": "https://empty.seoul.kr/product/list.html?cate_no=54",
    "긴소매 셔츠": "https://empty.seoul.kr/product/list.html?cate_no=101", 
    "스웨트 셔츠": "https://empty.seoul.kr/product/list.html?cate_no=77",
    "후드": "https://empty.seoul.kr/product/list.html?cate_no=64",
    "플리스": "https://empty.seoul.kr/product/list.html?cate_no=822",
    #BOTTOM
    "데님 팬츠": "https://empty.seoul.kr/product/list.html?cate_no=61",
    "팬츠": "https://empty.seoul.kr/product/list.html?cate_no=75",
    "스커트": "https://empty.seoul.kr/product/list.html?cate_no=95",
    #DRESS
    "원피스": "https://empty.seoul.kr/product/list.html?cate_no=59",
    #BAG
    "백팩": "https://empty.seoul.kr/product/list.html?cate_no=98",
    "토트백": "https://empty.seoul.kr/product/list.html?cate_no=88",
    "크로스백": "https://empty.seoul.kr/product/list.html?cate_no=99",
    #SHOES
    "스니커즈": "https://empty.seoul.kr/product/list.html?cate_no=113",
    "부츠": "https://empty.seoul.kr/product/list.html?cate_no=67",
    #HAT
    "캡모자": "https://empty.seoul.kr/product/list.html?cate_no=324",
    "비니": "https://empty.seoul.kr/product/list.html?cate_no=341"
}

CATEGORY_MAP = {
    #OUTER
    "숏 패딩": {"대분류": "OUTER", "중분류": "PADDING"},
    "코트": {"대분류": "OUTER", "중분류": "COAT"},
    "레더 자켓": {"대분류": "OUTER", "중분류": "JACKET"},
    "무스탕/퍼": {"대분류": "OUTER", "중분류": "JACKET"},
    #TOP
    "티셔츠": {"대분류": "TOP", "중분류": "TSHIRT"},
    "긴소매 셔츠": {"대분류": "TOP", "중분류": "LSHIRT"},
    "스웨트 셔츠": {"대분류": "TOP", "중분류": "SWEATSHIRT"},
    "후드": {"대분류": "TOP", "중분류": "HOODIE"},
    "플리스": {"대분류": "TOP", "중분류": "FLEECE"},
    #BOTTOM
    "데님 팬츠": {"대분류": "BOTTOM", "중분류": "DENIM"},
    "팬츠": {"대분류": "BOTTOM", "중분류": "PANTS"},
    "스커트": {"대분류": "BOTTOM", "중분류": "SKIRT"},
    #DRESS
    "드레스": {"대분류": "DRESS", "중분류": "ONE_PIECE"},
    #BAG
    "백팩": {"대분류": "BAG", "중분류": "BACKPACK"},
    "토트백": {"대분류": "BAG", "중분류": "TOTE"},
    "크로스백": {"대분류": "BAG", "중분류": "CROSSBODY"},
    #SHOES
    "스니커즈": {"대분류": "SHOES", "중분류": "SNEAKERS"},
    "부츠": {"대분류": "SHOES", "중분류": "BOOTS"},
    #HAT
    "볼캡": {"대분류": "HAT", "중분류": "CAP"},
    "비니": {"대분류": "HAT", "중분류": "BEANIE"}

}

LIST_CONTAINER_SELECTORS = ["ul.prdList", "ul.prdList.grid4", ".prdList"]

# ===============================
# JS: 상품 스냅샷 (URL/IMG는 "img를 감싸는 a"에서만!)
# ===============================
JS_EXTRACT = r"""
() => {
  const results = [];

  const itemSelectors = [
    "ul.prdList > li[id^='anchorBoxId_']",
    "ul.prdList > li",
    ".prdList > li",
    "ul.prdList.grid4 > li",
  ];

  let items = [];
  for (const sel of itemSelectors) {
    const found = Array.from(document.querySelectorAll(sel));
    if (found.length) { items = found; break; }
  }

  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();

  for (const item of items) {
    // ✅ 링크가 여러 개라서, "img를 포함한 a"만 선택
    const thumbCandidates = Array.from(item.querySelectorAll("div.thumbnail a[href^='/product/']"));
    const thumbLink = thumbCandidates.find(a => a.querySelector("img")) || null;

    let href = thumbLink?.getAttribute("href") || "";
    if (href && !href.startsWith("http")) href = new URL(href, location.origin).href;

    const img = thumbLink?.querySelector("img") || item.querySelector("div.thumbnail img");
    let imgUrl =
      img?.getAttribute("src") ||
      img?.getAttribute("data-src") ||
      img?.getAttribute("data-original") ||
      img?.getAttribute("ec-data-src") ||
      "";

    if (imgUrl && imgUrl.startsWith("//")) imgUrl = location.protocol + imgUrl;
    if (imgUrl && imgUrl.startsWith("/")) imgUrl = new URL(imgUrl, location.origin).href;

    const name = clean(img?.getAttribute("alt")) || clean(item.querySelector(".description .name a")?.textContent);

    // 브랜드는 사이트마다 다를 수 있어 fallback 여러 개
    let rawBrand =
        item.querySelector(".description ul.hee_brand li a")?.textContent ||
        item.querySelector(".description .brand a")?.textContent ||
        item.querySelector(".description .brand")?.textContent ||
        "";

    let brand = clean(rawBrand)
        .replace(/^브랜드\s*[:：]?\s*/i, "")
        .replace(/^brand\s*[:：]?\s*/i, "");

    // ✅ 가격/할인율: 라벨이 없어서 description 전체 텍스트에서 %/원 추출
    const desc = item.querySelector(".description") || item;
    const text = desc.textContent || "";

    const discountMatch = text.match(/(\d{1,3})\s*%/);
    const discount = discountMatch ? discountMatch[1] : "";

    // 원 단위 숫자 전부 추출(2개면 정가/할인가로 분리 가능)
    const priceMatches = Array.from(text.matchAll(/(\d[\d,]*)\s*원/g))
      .map(m => parseInt(m[1].replace(/,/g, ""), 10))
      .filter(n => Number.isFinite(n));

    // 일단 원문 숫자들을 그대로 넘기고, 파이썬에서 정가/할인가 판단을 더 안전하게 함
    results.push({
      brand,
      name,
      href,
      imgUrl,
      discount,
      prices: priceMatches
    });
  }

  return results;
}
"""

# ===============================
# JS: 페이지네이션 정보(최대 페이지/next 유무/현재 페이지)
# ===============================
JS_PAGING_INFO = r"""
() => {
  const toNum = (v) => {
    const n = parseInt(String(v || "").trim(), 10);
    return Number.isFinite(n) ? n : null;
  };

  const pageFromHref = (href) => {
    try {
      const u = new URL(href, location.origin);
      const p = u.searchParams.get("page");
      return p ? toNum(p) : null;
    } catch(e) {
      return null;
    }
  };

  const pageLinks = Array.from(document.querySelectorAll("a[href*='page=']"));
  const pages = pageLinks
    .map(a => pageFromHref(a.getAttribute("href") || ""))
    .filter(n => n !== null);

  const maxPage = pages.length ? Math.max(...pages) : 1;

  const nextCandidates = Array.from(document.querySelectorAll(
    "a.next, a[rel='next'], .ec-base-paginate a.next, .paginate a.next"
  ));

  const isActiveNext = (a) => {
    if (!a) return false;
    const href = (a.getAttribute("href") || "").trim().toLowerCase();
    if (!href || href === "#" || href.startsWith("javascript")) return false;
    const cls = (a.getAttribute("class") || "").toLowerCase();
    if (cls.includes("disabled")) return false;
    return true;
  };

  const hasNext = nextCandidates.some(isActiveNext);

  let currentPage = null;
  const selected =
    document.querySelector(".paginate li.selected a, .ec-base-paginate li.selected a, .pagination .active a");
  if (selected) currentPage = toNum(selected.textContent);

  if (!currentPage) {
    const u = new URL(location.href);
    const p = u.searchParams.get("page");
    currentPage = p ? toNum(p) : 1;
  }

  return { currentPage: currentPage || 1, maxPage, hasNext };
}
"""

# ===============================
def build_page_url(base_url, page_num):
    parts = urlsplit(base_url)
    q = parse_qs(parts.query)
    q.pop("page", None)
    if page_num > 1:
        q["page"] = [str(page_num)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q, doseq=True), ""))

def normalize_url(u):
    p = urlsplit(u)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

# ===============================
def scrape():
    rows = []
    global_seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=30)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for category, base_url in CATEGORIES.items():
            print(f"\n📂 {category}")
            page_num = 1
            no_new = 0

            while page_num <= MAX_PAGES_PER_CATEGORY:
                page.goto(build_page_url(base_url, page_num), wait_until="domcontentloaded")
                time.sleep(1)

                snapshot = page.evaluate(JS_EXTRACT)
                paging = page.evaluate(JS_PAGING_INFO)

                added = 0
                for it in snapshot:
                    href = normalize_url(it["href"])
                    if href in global_seen:
                        continue
                    global_seen.add(href)

                    prices = it["prices"]
                    discount = int(it["discount"]) if it["discount"] else None

                    if len(prices) >= 2:
                        original, sale = max(prices), min(prices)
                    elif len(prices) == 1:
                        sale = prices[0]
                        original = (
                            int(round(sale * 100 / (100 - discount), -1))
                            if discount else sale
                        )
                    else:
                        continue

                    rows.append({
                        "대분류": CATEGORY_MAP[category]["대분류"],
                        "중분류": CATEGORY_MAP[category]["중분류"],
                        "카테고리": category,
                        "브랜드": it["brand"],
                        "상품명": it["name"],
                        "정가": original,
                        "판매가": sale,
                        "할인율(%)": discount or "-",
                        "상품 URL": href,
                        "이미지 URL": it["imgUrl"],
                    })
                    added += 1

                print(f"  → page {page_num}, 신규 {added}개")

                if added == 0:
                    no_new += 1
                    if no_new >= NO_NEW_PAGES_LIMIT:
                        break
                else:
                    no_new = 0

                if not paging["hasNext"] and page_num >= paging["maxPage"]:
                    break

                page_num += 1

        browser.close()

    # ===============================
    # 대분류별 CSV 저장 (헤더 ❌)
    # ===============================
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    grouped = {}
    for r in rows:
        grouped.setdefault(r["대분류"], []).append(r)

    for major, items in grouped.items():
        with open(os.path.join(OUTPUT_DIR, f"{major}.csv"), "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writerows(items)

        print(f"✅ {major}.csv 저장 ({len(items)}개)")

# ===============================
if __name__ == "__main__":
    scrape()
