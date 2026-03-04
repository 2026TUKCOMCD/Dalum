import { authApi } from '../../api';
import type { GetDetailDupeSearchResponse } from '../../types/me/Me.types';

// 듀프 제품 검색 기록 상세 조회 API
const getDetailDupeSearch = async (
  searchId: number
): Promise<GetDetailDupeSearchResponse> => {
  const { data } = await authApi.get<GetDetailDupeSearchResponse>(
    `/api/v1/me/search-logs/${searchId}`
  );

  return data;
};

export default getDetailDupeSearch;
