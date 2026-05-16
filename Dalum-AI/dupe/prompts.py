# dupe/prompts.py
# 모든 CLIP 프롬프트 정의 — dupe.py, build_clip.py 양쪽이 이 파일만 참조
# 프롬프트 수정 시 이 파일만 변경하면 됨


# ─── 대분류 감지 프롬프트 ────────────────────────────────────────────────
CATEGORY_PROMPTS = {
    "TOP"   : "a pullover top worn as the main garment on the upper body without any front zipper, such as t-shirts, long sleeve shirts, crew-neck sweatshirts, knit sweaters, or pullover hoodies with a hood but no front zipper",
    "BOTTOM": "pants, jeans, shorts, skirt, or trousers worn on the lower body",
    "OUTER" : "outerwear worn as an outer layer over other clothing, such as coats, blazers, padded jackets, parkas, windbreakers, vests, cardigans, or zip-up hoodies that have a visible full-length front zipper",
    "DRESS" : "a dress, one-piece outfit, or jumpsuit",
    "BAG"   : "a bag, handbag, backpack, tote, or purse",
    "SHOES" : "shoes, sneakers, boots, sandals, or footwear",
    "HAT"   : "a hat, cap, beanie, beret, or headwear",
}

CATEGORY_NAMES = list(CATEGORY_PROMPTS.keys())
CATEGORY_TEXTS = list(CATEGORY_PROMPTS.values())


# ─── 중분류 감지 프롬프트 ────────────────────────────────────────────────
MIDDLE_CATEGORY_PROMPTS = {
    "TOP": {
        "TSHIRT"    : "a short-sleeve t-shirt, short-sleeve shirt, short-sleeve polo shirt, or sleeveless tank top — any top with sleeves ending above the elbow, or with no sleeves at all",
        "LSHIRT"    : "a long-sleeve t-shirt, long-sleeve shirt, or long-sleeve polo shirt with sleeves extending fully to the wrist",
        "SWEATSHIRT": "a crew-neck pullover sweatshirt with no hood and no front zipper, made of cotton fleece or terry fabric — also called 맨투맨",
        "HOODIE"    : "a pullover hoodie sweatshirt with an attached hood and drawstring cords — no front zipper, must be pulled over the head to wear",
        "KNIT"      : "a knit sweater or knitwear with clearly visible knitted stitch texture — includes crewneck knit, V-neck knit, turtleneck knit, polo knit, and sleeveless knit vest",
        "FLEECE"    : "a polar fleece or micro-fleece top with a distinctively soft fuzzy brushed surface texture, typically a half-zip fleece or crew-neck fleece pullover",
        "BLOUSE"    : "a women's blouse or feminine lightweight top made of chiffon, silk, or delicate woven fabric — often featuring ruffles, bows, lace, or other elegant decorative details",
        "ETC_TOP"   : "a top or upper-body garment that does not clearly match any other top category",
    },
    "OUTER": {
        "COAT"     : "a coat, trench coat, or structured long outerwear extending below mid-thigh — including short coat, half coat, long coat, single-breasted wool coat, double-breasted coat, and belted trench coat made of wool, cashmere, or woven fabric",
        "PADDING"  : "a puffer jacket or down jacket with clearly visible stitched quilted sections and padded insulation filling — available as short puffer, long puffer, or ultra-lightweight packable jacket",
        "JACKET"   : "a leather jacket, biker jacket, denim jacket, varsity jacket, fur jacket, mustang jacket, blazer, training jacket, coach jacket with snap closure, fleece jacket, quilted jacket, work jacket, overshirt worn as outer layer, or hooded outer shell jacket — any short structured jacket with a defined collar made of leather, denim, fleece, nylon, polyester, or woven fabric",
        "JUMPER"   : "a blouson jacket with a puffed loose body and gathered elastic hem band, field jacket with multiple cargo pockets, anorak pullover, or military utility jacket — characterized by a balloon-like silhouette above an elastic hem, cargo pockets, drawstring hem, or military field styling",
        "VEST"     : "a sleeveless vest or padded vest with no arms whatsoever — both arms are completely exposed while the chest and shoulders remain covered",
        "CARDIGAN" : "a front-opening knitted cardigan with clearly visible knit or crochet stitch texture that fully opens with buttons, made of wool or acrylic knitwear — not a woven fabric jacket",
        "ZIP_UP"   : "a zip-up hoodie or zip-up sweatshirt made of soft cotton fleece, terry cloth, or knit fabric with a full-length front zipper — a casual sporty top worn as a light layer, clearly not a structured outer jacket or shell",
        "ETC_OUTER": "a miscellaneous outerwear item that does not clearly fit any other outer category such as coat, jacket, padding, jumper, vest, cardigan, or zip-up",
    },
    "BOTTOM": {
        "DENIM"      : "jeans or denim pants made of blue or black denim fabric — including skinny jeans, straight jeans, wide-leg jeans, and cropped jeans",
        "SLACKS"     : "formal dress pants or slacks with a tailored smooth silhouette, including wide-leg slacks and suit trousers",
        "PANTS"      : "casual pants or trousers — including cotton pants, cargo pants with side pockets, slim pants, straight-leg pants, wide-leg pants, bootcut pants, training pants, and sweatpants",
        "SHORT_PANTS": "shorts or short pants that end well above the knee",
        "SKIRT"      : "a skirt of any length — including denim skirt, mini skirt ending above the knee, midi skirt ending below the knee, and maxi skirt reaching the ankle",
        "ETC_BOTTOM" : "bottoms or pants that do not clearly fit any other bottom category",
    },
    "DRESS": {
        "ONE_PIECE" : "a dress or one-piece outfit with a connected top and skirt — including casual mini dress, midi dress, maxi dress, wrap dress, shirt dress, and knit dress",
        "JUMPSUIT"  : "a jumpsuit or playsuit with a connected top and pants in one piece — including wide-leg jumpsuit, slim jumpsuit, and short-sleeve playsuit",
        "ETC_DRESS" : "a one-piece garment that does not clearly fit a dress or jumpsuit category",
    },
    "BAG": {
        "BACKPACK" : "a backpack or rucksack with two shoulder straps worn symmetrically on the back",
        "CROSSBODY": "a small crossbody bag or messenger bag worn diagonally across the body on a single long strap",
        "WAIST"    : "a fanny pack or belt bag worn strapped around the waist or hips",
        "SHOULDER" : "a shoulder bag with a medium-length strap carried on one shoulder",
        "TOTE"     : "a large open-top tote bag or eco bag with two short handles, carried by hand or over one shoulder",
        "ETC_BAG"  : "a small mini bag, duffle bag, Boston bag, laptop bag, clutch, or any other bag type",
    },
    "SHOES": {
        "SNEAKERS"      : "sneakers or athletic shoes — including high-top sneakers, low-top sneakers, slip-on sneakers, running shoes, and casual sports shoes with rubber soles",
        "BOOTS"         : "boots of any height — including ankle boots, Chelsea boots, worker boots, combat boots, winter fur-lined boots, rain boots, short boots, and mid-calf boots",
        "LOAFER"        : "dress shoes or loafers with a low flat heel and closed toe — including leather Oxford shoes, penny loafers, and formal leather shoes",
        "SANDAL_SLIPPER": "sandals or slippers with an open toe or open back that expose part of the foot",
        "ETC_SHOES"     : "flat shoes, derby lace-up shoes, high heels, pumps, or other shoe styles not matching above categories",
    },
    "HAT": {
        "CAP"      : "a baseball cap or camp cap with a structured crown and a stiff curved brim only at the front",
        "SUNCAP"   : "a sun visor or sun cap with only a front brim and no fabric covering the top of the head — the crown is entirely open",
        "BEANIE"   : "a knitted beanie hat or watch cap that fits snugly around the head and ears with no brim at all",
        "BALACLAVA": "a balaclava or ski mask that covers the entire head and neck leaving only the eyes or face partially exposed",
        "TROOPER"  : "a trooper or trapper hat with padded ear flaps that fold down to cover the ears and sides of the face",
        "FEDORA"   : "a fedora hat with a wide brim and a creased or pinched felt crown, made of felt or straw",
        "BERET"    : "a flat round soft beret that sits tilted on the head with no brim whatsoever",
        "BUCKET"   : "a bucket hat with a soft round crown and a wide downward-sloping brim all the way around the entire hat",
        "ETC_HAT"  : "a hat style that does not fit any other specific hat category",
    },
}

# ─── 색상 프롬프트 (37개) ─────────────────────────────────────────────
COLOR_PROMPTS = [
    # 무채색 계열
    "a pure jet black clothing with no visible warm or cool color tone",
    "a very dark charcoal or dark anthracite gray clothing, almost black",
    "a dark espresso brown or near-black very dark brown clothing",
    "a slate gray or cool medium-dark gray clothing",
    "a dark gray clothing",
    "a medium gray clothing",
    "a light gray or silver clothing",
    "a white or bright ivory clothing",
    "a cream or soft off-white clothing",
    # 베이지·브라운 계열
    "a beige or sand colored clothing",
    "a tan or khaki colored clothing",
    "a warm medium camel or light brown clothing",
    "a warm dark chocolate brown or cocoa brown clothing",
    "a rust, burnt orange, or terracotta colored clothing",
    # 옐로 계열
    "a mustard or golden yellow clothing",
    "a bright yellow clothing",
    # 오렌지·레드 계열
    "a vivid orange clothing",
    "a coral or salmon pink-orange clothing",
    "a red clothing",
    "a burgundy, wine, or deep red clothing",
    # 핑크 계열
    "a dusty rose, mauve, or muted pink clothing",
    "a bright or pastel pink clothing",
    # 블루 계열
    "a midnight navy or very dark navy blue clothing",
    "a navy blue or dark blue clothing",
    "a royal blue or cobalt blue clothing",
    "a medium blue clothing",
    "a teal or cyan blue-green clothing",
    "a sky blue or baby blue clothing",
    # 그린 계열
    "a dark olive or military khaki green clothing",
    "a medium olive or army green clothing",
    "a vivid deep forest or hunter green clothing",
    "a bright kelly or emerald green clothing",
    "a medium green clothing",
    "a mint or light pastel green clothing",
    # 퍼플 계열
    "a purple or violet clothing",
    "a lavender or lilac light purple clothing",
    # 기타
    "a multicolor, patterned, or color-blocked clothing",
]

# ─── 디자인 프롬프트 (59개) ───────────────────────────────────────────
DESIGN_PROMPTS = {
    # 무지 / 단색
    "solid"        : "a plain solid color clothing with uniform color and no visible pattern, print, or texture detail",
    "color_block"  : "a clothing with two or more distinct solid color block panels separated by clear boundaries",
    "gradient"     : "a clothing with gradient or ombre color transition effect blending from one color to another",
    # 패턴
    "striped"      : "a clothing with horizontal, vertical, or diagonal stripe lines pattern",
    "checkered"    : "a clothing with check, plaid, tartan, or gingham grid pattern",
    "argyle"       : "a clothing with argyle overlapping diamond rhombus pattern",
    "houndstooth"  : "a clothing with houndstooth broken check or dogtooth pattern",
    "polka_dot"    : "a clothing with polka dot or circle spot pattern",
    "geometric"    : "a clothing with abstract geometric shapes, triangles, or angular pattern",
    "floral"       : "a clothing with floral, flower, or botanical print pattern",
    "paisley"      : "a clothing with paisley ornate teardrop swirl pattern",
    "animal_print" : "a clothing with animal print such as leopard spots, zebra stripes, or snake skin",
    "camouflage"   : "a clothing with military camouflage or camo pattern",
    "tie_dye"      : "a clothing with tie dye swirl or spiral color pattern",
    # 프린트
    "logo_text"    : "a clothing with brand logo, text lettering, or word print",
    "graphic"      : "a clothing with a large printed graphic artwork or abstract illustration on the front or back",
    "character"    : "a clothing with cartoon characters, anime figures, mascots, or pop culture icons printed on it",
    "heart"        : "a clothing with heart shape motif print or emblem",
    "star"         : "a clothing with star shape motif print or emblem",
    # 장식
    "embroidery"   : "a clothing with hand or machine embroidery stitched detail or patch",
    "rhinestone"   : "a clothing with rhinestones, studs, crystals, or jewel embellishments",
    "ribbon_bow"   : "a clothing with ribbon, bow, or tied decorative detail",
    "fringe"       : "a clothing with hanging fringe, tassel, or frayed edge detail",
    "metallic"     : "a clothing with shiny metallic sequins, glitter, or holographic surface",
    "pleated"      : "a clothing with pleated folds, ruffles, or gathered fabric detail",
    # 특수 실루엣 (패턴+구조 혼합)
    "varsity"      : "a varsity or baseball stadium jacket with contrast color sleeves and ribbed collar",
    "quilted"      : "a quilted jacket or clothing with visible diamond or box stitching sewn through padded layers",
    # 소재
    "washed"       : "a washed, distressed, acid-washed, or vintage-treated worn-look clothing",
    "nylon"        : "a lightweight nylon or polyester windbreaker, shell jacket, or technical outerwear with a smooth or ripstop synthetic surface",
    "denim"        : "a denim fabric clothing such as jeans, denim jacket, or chambray shirt",
    "knit"         : "a knit or cable knit sweater, cardigan, or knitwear with visible knitted texture",
    "leather"      : "a smooth leather or faux leather jacket, coat, or pants with visible leather surface texture, clearly not woven fabric",
    "fur"          : "a clothing made of fluffy fur, faux fur, or shearling with soft voluminous pile",
    "fleece"       : "a clothing made of soft cozy fleece or sherpa material",
    "wool"         : "a wool, cashmere, tweed, or woolen fabric clothing with a woven or felted soft texture",
    "velvet"       : "a clothing made of velvet or velour fabric with a soft plush pile surface",
    "silk_satin"   : "a clothing made of glossy silk, satin, or lustrous shiny fabric",
    "linen"        : "a clothing made of breathable linen or ramie natural fabric with a slightly rough texture",
    "sheer"        : "a sheer, transparent, or semi-transparent mesh or chiffon clothing",
    "lace"         : "a clothing with delicate lace fabric or lace trim detail",

    # ── 형태 / 실루엣 (19개) ──────────────────────────────────────────────

    # 핏 / 볼륨
    "oversized"        : "an oversized or boxy clothing with extra volume, dropped shoulders, and a very loose wide silhouette that does not hug the body",
    "slim_fitted"      : "a slim-fit, form-fitting, or body-hugging clothing that closely follows the body contour with structured narrow shoulders",
    "cropped"          : "a cropped or cut-off top, jacket, or sweater that ends at or above the natural waist, exposing the midriff",

    # 길이
    "longline"         : "a longline or extended-length coat or jacket with a hemline that falls to mid-thigh, knee, or lower",
    "mini_length"      : "a very short mini skirt, mini dress, or short shorts with a hemline ending well above the knee",

    # 칼라 / 넥라인
    "hooded"           : "a clothing with an attached hood or drawstring hoodie neckline that can be pulled up over the head",
    "high_neck"        : "a clothing with a high turtleneck, roll neck, mock neck, or funnel neck collar that rises up around the throat",
    "lapel_collar"     : "a jacket or coat with distinct wide notch lapels, peak lapels, or a shawl collar forming a deep V-shape at the chest",
    "collarless"       : "a collarless jacket, blazer, or coat with a clean round crew neck or mandarin band collar and no visible lapels",
    "off_shoulder"     : "a clothing with an off-shoulder, one-shoulder, or bardot neckline that exposes both or one shoulder and the collarbone",

    # 여밈 / 구조
    "double_breasted"  : "a double-breasted coat, jacket, or blazer with two parallel vertical rows of buttons arranged symmetrically down the center front",
    "belted"           : "a coat, jacket, or dress with a waist belt, self-tie fabric sash, or drawstring cord that cinches and visually defines the waist",
    "zip_front"        : "a jacket, hoodie, or sweatshirt with a visible full-length front center zipper closure running from hem to neck",
    "open_front"       : "an open-front cardigan, duster coat, or longline jacket with no buttons or zip, with front panels hanging open freely",

    # 아우터 전용 실루엣
    "bomber_silhouette": "a bomber or flight jacket with a short body ending at the hip, a ribbed elastic waistband at the hem, and ribbed cuffs at the wrists",
    "moto_biker"       : "a moto or biker jacket with an asymmetric diagonal zip across the chest, stiff structured shoulders, and a close-fitted body",

    # 하의 실루엣
    "wide_leg_bottom"  : "wide-leg, palazzo, or baggy pants or trousers with a very loose voluminous silhouette flowing from hip to ankle",
    "slim_leg_bottom"  : "slim-fit, skinny, or tapered pants or jeans that fit snugly around the thigh and taper toward the ankle",
    "flared_bottom"    : "flared, bootcut pants, or an A-line or circle skirt that flares outward from the knee or waist downward",
}

DESIGN_NAMES = list(DESIGN_PROMPTS.keys())
DESIGN_TEXTS = list(DESIGN_PROMPTS.values())
