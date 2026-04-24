from dataclasses import dataclass
from enum import Enum


# ============================
# Cut Type 정의
# ============================

class CutType(str, Enum):
    NONE = "none"
    HIP_BELOW = "hip_below"
    HIP_ABOVE = "hip_above"
    FACE_ONLY = "face_only"
    SHORT_BOTTOM = "short_bottom"


@dataclass
class CutPolicy:
    cut_type: CutType
    margin_ratio: float = 0.0
    dynamic_ratio: float | None = None


# ============================
# 정책 헬퍼
# ============================

def TOP_POLICY(ratio: float = 0.60):
    return CutPolicy(
        cut_type=CutType.HIP_BELOW,
        dynamic_ratio=ratio
    )

def OUTER_POLICY(margin: float = 0.02):
    return CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=margin
    )

def BOTTOM_POLICY():
    return CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0
    )

def NO_CUT():
    return CutPolicy(CutType.NONE)

def FACE_POLICY():
    return CutPolicy(CutType.FACE_ONLY)

def KNIT_POLICY():
    return CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,   # 살짝 위에서 컷
        dynamic_ratio=None   # 🔥 dynamic 제거
    )
def SHORT_BOTTOM_POLICY():
    return CutPolicy(
        cut_type=CutType.SHORT_BOTTOM,
        margin_ratio=0.03
    )
# =========================================================
# CATEGORY → CUT POLICY
# =========================================================

CATEGORY_CUT_POLICY = {

    # =====================================================
    # OUTER
    # =====================================================

    # PADDING
    "숏 패딩": OUTER_POLICY(),
    "롱 패딩": NO_CUT(),
    "경량 패딩": OUTER_POLICY(),

    # COAT
    "코트": NO_CUT(),
    "트렌치 코트": NO_CUT(),
    "숏 코트": NO_CUT(),
    "하프 코트": NO_CUT(),
    "롱 코트": NO_CUT(),
    "싱글 코트": NO_CUT(),
    "더블 코트": NO_CUT(),

    # JACKET
    "바시티 자켓": OUTER_POLICY(),
    "데님 자켓": OUTER_POLICY(),
    "무스탕": OUTER_POLICY(),
    "퍼 자켓": OUTER_POLICY(),
    "무스탕/퍼": OUTER_POLICY(),
    "레더 자켓": OUTER_POLICY(),
    "블레이저": OUTER_POLICY(),
    "퀄팅 자켓": OUTER_POLICY(),
    "워크 자켓": OUTER_POLICY(),
    "오버 셔츠": OUTER_POLICY(),
    "후드 자켓": OUTER_POLICY(),
    "트레이닝 자켓": OUTER_POLICY(),
    "코치 자켓": OUTER_POLICY(),
    "폴리스 자켓": OUTER_POLICY(),
    "기타 자켓": OUTER_POLICY(),

    # JUMPER
    "블루종": OUTER_POLICY(),
    "야상": OUTER_POLICY(),
    "바람막이": OUTER_POLICY(),
    "아노락": OUTER_POLICY(),
    "기타 점퍼": OUTER_POLICY(),

    # VEST
    "베스트": OUTER_POLICY(),
    "패딩 베스트": OUTER_POLICY(),

    # CARDIGAN
    "가디건": OUTER_POLICY(),

    # ZIP_UP
    "후드 집업": OUTER_POLICY(),
    "집업": OUTER_POLICY(),
    "니트 집업": OUTER_POLICY(),

    # ETC_OUTER
    "기타 아우터": OUTER_POLICY(),

    # =====================================================
    # TOP
    # =====================================================

    # TSHIRT
    "티셔츠": TOP_POLICY(0.60),
    "반소매 셔츠": TOP_POLICY(0.60),
    "반소매 카라 셔츠": TOP_POLICY(0.60),
    "슬리브리스": TOP_POLICY(0.58),

    # LSHIRT
    "긴소매 티셔츠": TOP_POLICY(0.60),
    "긴소매 셔츠": TOP_POLICY(0.60),
    "긴소매 카라 셔츠": TOP_POLICY(0.60),

    # SWEATSHIRT
    "스웨트 셔츠": TOP_POLICY(0.62),

    # HOODIE
    "후드": TOP_POLICY(0.68),

    # KNIT
    "니트": KNIT_POLICY(),
    "크루넥 니트": KNIT_POLICY(),
    "브이넥 니트": KNIT_POLICY(),
    "터틀넥 니트": KNIT_POLICY(),
    "폴로 니트": KNIT_POLICY(),
    "니트 베스트": KNIT_POLICY(),
    "기타 니트": KNIT_POLICY(),

    # FLEECE
    "플리스": TOP_POLICY(0.62),

    # BLOUSE
    "블라우스": TOP_POLICY(0.65),

    # ETC_TOP
    "기타 상의": TOP_POLICY(0.60),

    # =====================================================
    # BOTTOM
    # =====================================================

    "데님 팬츠": BOTTOM_POLICY(),
    "슬랙스": BOTTOM_POLICY(),

    "코튼 팬츠": BOTTOM_POLICY(),
    "카고 팬츠": BOTTOM_POLICY(),
    "슬림 팬트": BOTTOM_POLICY(),
    "스트라이트 팬츠": BOTTOM_POLICY(),
    "와이드 팬츠": BOTTOM_POLICY(),
    "부츠컷": BOTTOM_POLICY(),
    "트레이닝 팬츠": BOTTOM_POLICY(),
    "스웨트 팬츠": BOTTOM_POLICY(),

    "숏 팬츠": SHORT_BOTTOM_POLICY(),

    "데님 스커트": BOTTOM_POLICY(),
    "미니 스커트": BOTTOM_POLICY(),
    "미디 스커트": BOTTOM_POLICY(),
    "롱 스커트": BOTTOM_POLICY(),

    "기타 팬츠": BOTTOM_POLICY(),

    # =====================================================
    # DRESS
    # =====================================================

    "원피스": NO_CUT(),
    "미디 원피스": NO_CUT(),
    "맥시 원피스": NO_CUT(),
    "미니 원피스": NO_CUT(),

    # =====================================================
    # HAT
    # =====================================================

    "볼캡": FACE_POLICY(),
    "캠프캡": FACE_POLICY(),
    "선캡": FACE_POLICY(),
    "비니": FACE_POLICY(),
    "워치캡": FACE_POLICY(),
    "바라클라바": FACE_POLICY(),
    "트루퍼": FACE_POLICY(),
    "페도라": FACE_POLICY(),
    "베레모": FACE_POLICY(),
    "버킷햇": FACE_POLICY(),
    "기타 모자": FACE_POLICY(),
}
