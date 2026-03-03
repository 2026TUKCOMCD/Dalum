import { authApi } from '../../api';
import type { RecommendStylingResponse } from '../../types/stylings/Styling.types';

// 스타일링 추천 API
const recommendStyling = async (
  targetProductId: number
): Promise<RecommendStylingResponse> => {
  const { data } = await authApi.post<RecommendStylingResponse>(
    `/api/v1/stylings/recommend`,
    null,
    { params: { targetProductId } }
  );

  return data;
};

export default recommendStyling;
