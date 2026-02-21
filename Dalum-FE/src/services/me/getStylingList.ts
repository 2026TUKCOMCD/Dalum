import { authApi } from "../../api";
import type { GetStylingListResponse } from "../../types/me/Me.types";

// 저장한 스타일링 목록 조회 API
const getStylingList = async (): Promise<GetStylingListResponse> => {
  const { data } = await authApi.get<GetStylingListResponse>(
    "/api/v1/me/stylings",
  );

  return data;
};

export default getStylingList;
