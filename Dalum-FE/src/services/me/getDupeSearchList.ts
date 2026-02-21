import { authApi } from "../../api";
import type { GetDupeSearchListResponse } from "../../types/me/Me.types";

// 듀프 제품 검색 기록 조회 API
const getDupeSearchList = async (): Promise<GetDupeSearchListResponse> => {
  const { data } = await authApi.get<GetDupeSearchListResponse>(
    "/api/v1/me/search-logs",
  );

  return data;
};

export default getDupeSearchList;
