import { authApi } from "../../api";
import type { GetLikeListResponse } from "../../types/me/Me.types";

// 좋아요한 상품 조회 API
const getLikeList = async (): Promise<GetLikeListResponse> => {
  const { data } = await authApi.get<GetLikeListResponse>("/api/v1/me/likes");

  return data;
};

export default getLikeList;
