import { authApi } from '../../api';
import type { GetDetailStylingResponse } from '../../types/stylings/Styling.types';

// 저장한 스타일링 상세 조회 API
const getDetailStyling = async (
  stylingId: number
): Promise<GetDetailStylingResponse> => {
  const { data } = await authApi.get<GetDetailStylingResponse>(
    `/api/v1/me/stylings/${stylingId}`
  );

  return data;
};

export default getDetailStyling;
