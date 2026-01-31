#이미지 컷 정책 코드
from dataclasses import dataclass
from enum import Enum


class CutType(str, Enum):
    NONE = "none" # 컷 없음
    HIP_BELOW = "hip_below" # 허리 아래 제거
    HIP_ABOVE = "hip_above"   # 나중에 BOTTOM용
    FACE_ONLY = "face_only"

@dataclass
class CutPolicy:
    cut_type: CutType
    margin_ratio: float = 0.0

# =========================================================
# CATEGORY → CUT POLICY
#
# 규칙:
# - dict에 없으면 기본값 = CutType.NONE
# - 얼굴 제거는 별도 로직 (모델 착샷이면 항상 수행)
# - 여기서는 "추가 컷(하체 제거)"만 정의
# - margin_ratio 해석
#   -0.08 → hip보다 위쪽으로 8%
#   -0.0 → hip 기준
#   +0.03 → hip보다 아래 (거의 안 씀)
# =========================================================

CATEGORY_CUT_POLICY = {

    # OUTER / PADDING
    "야상": CutPolicy(CutType.NONE),

    "경량패딩": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "숏패딩": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "다운": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "패딩 베스트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "롱패딩": CutPolicy(CutType.NONE),

    # OUTER / COAT
    "트렌치/맥코트": CutPolicy(CutType.NONE),
    "트렌치 코트": CutPolicy(CutType.NONE),
    "숏코트": CutPolicy(CutType.NONE),
    "하프코트": CutPolicy(CutType.NONE),
    "롱코트": CutPolicy(CutType.NONE),
    "싱글코트": CutPolicy(CutType.NONE),
    "더블코트": CutPolicy(CutType.NONE),

    # OUTER / JACKET
    "블루종": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "바시티": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "바시티 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "데님 재킷": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "데님 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "퍼 재킷": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "퍼 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "트레이닝 재킷": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "트레이닝 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "점퍼": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "바람막이": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "아노락": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "나일론/코치 재킷": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "코치 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "레더 재킷": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "레더 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "블레이저": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "무스탕": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "무스탕·퍼": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "퀼팅 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "워크 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "오버셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "후드 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "기타 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    # OUTER / VEST
    "베스트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    # OUTER / CARDIGAN
    "카디건": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    # OUTER / HOODED_ZIP_UP
    "후드 집업": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "집업": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "니트 집업": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    # OUTER / FLEECE_JACKET
    "플리스 자켓": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    # TOP (전부 컷 없음)
    "반소매 티셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "긴소매 티셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "피케/카라 티셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "반소매 카라 티셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "긴소매 카라 티셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "반소매 셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "긴소매 셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "블라우스": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "스웨트셔츠": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "맨투맨": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "후드": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "후드": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "크루넥 니트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "브이넥 니트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "터틀넥 니트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "폴로 니트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "니트 베스트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "니트 후드": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "기타 니트": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),

    "플리스": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "슬리브리스": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),
    "기타 상의": CutPolicy(
        cut_type=CutType.HIP_BELOW,
        margin_ratio=0.01,
    ),


    # BOTTOM (컷 없음)
    "데님 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "슬랙스": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "코튼 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "카고 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "슬림 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "스트레이트 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "와이드 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "부츠컷": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "트레이닝 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "스웨트팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "쇼트": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "숏 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "레깅스": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "데님 스커트": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "미니 스커트": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "미디 스커트": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "롱 스커트": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "오버올": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "기타 팬츠": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),
    "기타 하의": CutPolicy(
        cut_type=CutType.HIP_ABOVE,
        margin_ratio=0.0,
    ),

    # DRESS (컷 없음)
    "원피스": CutPolicy(CutType.NONE),
    "수트 셋업": CutPolicy(CutType.NONE),
    "수트": CutPolicy(CutType.NONE),
    "점프수트": CutPolicy(CutType.NONE),
    "스웻/트레이닝 셋업": CutPolicy(CutType.NONE),
    "홈웨어 세트": CutPolicy(CutType.NONE),
    "로브": CutPolicy(CutType.NONE),
    "기타 상하의 셋업": CutPolicy(CutType.NONE),


    # BAG / SHOES /(컷 없음)
    "백팩": CutPolicy(CutType.NONE),
    "크로스백": CutPolicy(CutType.NONE),
    "메신저백": CutPolicy(CutType.NONE),
    "웨이스트백": CutPolicy(CutType.NONE),
    "숄더백": CutPolicy(CutType.NONE),
    "토트백": CutPolicy(CutType.NONE),
    "에코백": CutPolicy(CutType.NONE),
    "클러치": CutPolicy(CutType.NONE),

    "스니커즈": CutPolicy(CutType.NONE),
    "부츠": CutPolicy(CutType.NONE),
    "워커": CutPolicy(CutType.NONE),
    "로퍼": CutPolicy(CutType.NONE),
    "구두": CutPolicy(CutType.NONE),
    "샌들": CutPolicy(CutType.NONE),
    "슬리퍼": CutPolicy(CutType.NONE),
    "기능화": CutPolicy(CutType.NONE),

    # HAT
    "캡모자": CutPolicy(CutType.FACE_ONLY),
    "볼캡": CutPolicy(CutType.FACE_ONLY),
    "비니": CutPolicy(CutType.FACE_ONLY),
    "바라클라바": CutPolicy(CutType.FACE_ONLY),
    "트루퍼": CutPolicy(CutType.FACE_ONLY),
    "페도라": CutPolicy(CutType.FACE_ONLY),
    "베레모": CutPolicy(CutType.FACE_ONLY),
    "버킷햇": CutPolicy(CutType.FACE_ONLY),
    "기타모자": CutPolicy(CutType.FACE_ONLY),
}
