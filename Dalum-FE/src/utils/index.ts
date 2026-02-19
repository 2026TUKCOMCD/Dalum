import type { SearchDupeProductsRequest } from "../types/search/Search.types";

// 듀프 제품 검색 요청 폼 형태로 변환하는 유틸
export const toFormData = (req: SearchDupeProductsRequest) => {
  const fd = new FormData();

  fd.append("image", req.image);

  if (req.brand?.trim()) fd.append("brand", req.brand.trim());
  if (typeof req.minPrice === "number")
    fd.append("minPrice", String(req.minPrice));
  if (typeof req.maxPrice === "number")
    fd.append("maxPrice", String(req.maxPrice));

  return fd;
};
