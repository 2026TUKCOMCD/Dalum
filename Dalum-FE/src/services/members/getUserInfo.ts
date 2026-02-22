import { authApi } from "../../api";
import type { GetUserInfoResponse } from "../../types/members/Member.types";

// 유저 정보 조회 API
const getUserInfo = async (): Promise<GetUserInfoResponse> => {
  const { data } = await authApi.get<GetUserInfoResponse>("/api/v1/members/me");

  return data;
};

export default getUserInfo;
