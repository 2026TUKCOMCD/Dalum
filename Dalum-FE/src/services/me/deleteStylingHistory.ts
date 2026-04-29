import { authApi } from '../../api';
import type { DeleteHistoryResponse } from '../../types/me/Me.types';

// 저장한 스타일링 삭제 API
const deleteStylingHistory = async (
  stylingId: number
): Promise<DeleteHistoryResponse> => {
  const { data } = await authApi.delete<DeleteHistoryResponse>(
    `/api/v1/me/stylings/${stylingId}`
  );

  return data;
};

export default deleteStylingHistory;
