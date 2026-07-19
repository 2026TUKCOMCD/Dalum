import type { PriceRange } from '../types/search/Search.types';

export const onboardingData = [
  {
    image: '/image/onboarding_1.png',
    title: '이미지 업로드 한 번으로\n손쉽게 듀프 제품 검색하기',
    description:
      '제품 이미지를 업로드하고 세부 사항을 설정하면\n조건에 맞는 듀프 제품 리스트를 받을 수 있습니다.',
  },
  {
    image: '/image/onboarding_2.png',
    title: '마음에 드는 제품은\n좋아요를 눌러 저장하기',
    description:
      '좋아요를 누른 제품은 마이 페이지에서\n스타일링 추천을 받을 수 있습니다.',
  },
  {
    image: '/image/onboarding_3.png',
    title: '좋아하는 제품에 어울리는\n스타일링 추천받기',
    description:
      '마음에 드는 듀프 제품에 어울리는 제품을\n종류 별로 추천 받을 수 있습니다.',
  },
];

export const guideData = [
  {
    image: '/image/guide_1.png',
    description:
      '‘좋아요’를 눌러 마음에 드는 제품을 저장할 수 있습니다.\n좋아요한 제품은 마이 페이지에서 스타일링 추천을 받을 수 있습니다.',
  },
  {
    image: '/image/guide_2.png',
    description:
      '‘유사도 확인’ 버튼을 눌러 업로드한 이미지와 듀프 제품의\n닮음 지수를 차트 형태로 확인할 수 있습니다.',
  },
  {
    image: '/image/guide_3.png',
    description:
      '‘구매 링크’ 버튼을 눌러 듀프 제품의 판매처로 이동할 수 있습니다.\n듀프 제품의 자세한 정보는 판매처에서 확인 가능합니다.',
  },
];

export const priceOptions = [
  '50,000원 미만',
  '50,000원 이상 ~ 100,000원 미만',
  '100,000원 이상 ~ 200,000원 미만',
  '200,000원 이상',
  '상관 없음',
];

export const PRICE_RANGE_MAP: Record<string, PriceRange> = {
  '50,000원 미만': { maxPrice: 49999 },
  '50,000원 이상 ~ 100,000원 미만': { minPrice: 50000, maxPrice: 99999 },
  '100,000원 이상 ~ 200,000원 미만': { minPrice: 100000, maxPrice: 199999 },
  '200,000원 이상': { minPrice: 200000 },
  '상관 없음': {},
};

export const CATEGORY_MAP: Record<string, string[]> = {
  BAG: ['HAT', 'OUTER', 'TOP', 'BOTTOM', 'SHOES'],
  TOP: ['HAT', 'OUTER', 'BOTTOM', 'SHOES', 'BAG'],
  BOTTOM: ['HAT', 'OUTER', 'TOP', 'SHOES', 'BAG'],
  OUTER: ['HAT', 'TOP', 'BOTTOM', 'SHOES', 'BAG'],
  DRESS: ['HAT', 'SHOES', 'BAG'],
  SHOES: ['HAT', 'OUTER', 'TOP', 'BOTTOM', 'BAG'],
  HAT: ['OUTER', 'TOP', 'BOTTOM', 'SHOES', 'BAG'],
};

export const CATEGORY_LABEL_MAP: Record<string, string> = {
  HAT: '모자',
  OUTER: '아우터',
  TOP: '상의',
  BOTTOM: '하의',
  SHOES: '신발',
  BAG: '가방',
  DRESS: '한벌옷',
};

export const scoreOptions = [
  '전체',
  '90점 이상',
  '80점 이상',
  '70점 이상',
  '60점 이상',
];

export const SCORE_THRESHOLD_MAP: Record<string, number> = {
  전체: 0,
  '90점 이상': 90,
  '80점 이상': 80,
  '70점 이상': 70,
  '60점 이상': 60,
};

export const USER_TYPE_MAP: Record<string, string> = {
  KAKAO: '카카오',
  GOOGLE: '구글',
  TEST: '테스트',
};
