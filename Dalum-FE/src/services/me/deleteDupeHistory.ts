import { authApi } from '../../api';
import type { DeleteHistoryResponse } from '../../types/me/Me.types';

// 듀프 제품 검색 기록 삭제 API
const deleteDupeHistory = async (
  searchId: number
): Promise<DeleteHistoryResponse> => {
  const { data } = await authApi.delete<DeleteHistoryResponse>(
    `/api/v1/me/search-logs/${searchId}`
  );

  return data;
};

export default deleteDupeHistory;
