import { authApi } from '../../api';
import type { ToggleLikeResponse } from '../../types/products/Product.types';

// 좋아요 토글 API
const toggleLike = async (productId: number): Promise<ToggleLikeResponse> => {
  const { data } = await authApi.post<ToggleLikeResponse>(
    `/api/v1/products/${productId}/likes`
  );

  return data;
};

export default toggleLike;
