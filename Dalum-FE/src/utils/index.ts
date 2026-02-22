import type { DupeSearchItem, StylingItem } from '../types/me/Me.types';
import type { SearchDupeProductsRequest } from '../types/search/Search.types';

// 듀프 제품 검색 요청 폼 형태로 변환하는 유틸
export const toFormData = (req: SearchDupeProductsRequest) => {
  const fd = new FormData();

  fd.append('image', req.image);

  if (req.brand?.trim()) fd.append('brand', req.brand.trim());
  if (typeof req.minPrice === 'number')
    fd.append('minPrice', String(req.minPrice));
  if (typeof req.maxPrice === 'number')
    fd.append('maxPrice', String(req.maxPrice));

  return fd;
};

// 날짜 형식 변환 유틸 (yyyy.mm.dd.(day) hh:mm 형식)
export const formatDate = (date: Date) => {
  date.setHours(date.getHours() + 9);

  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');

  const hour = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');

  const dayLabels = ['일', '월', '화', '수', '목', '금', '토'];
  const day = dayLabels[date.getDay()];

  return `${y}.${m}.${d}.(${day}) ${hour}:${min}`;
};

export const isDupeSearchItem = (
  item: DupeSearchItem | StylingItem
): item is DupeSearchItem => 'searchLogId' in item;
