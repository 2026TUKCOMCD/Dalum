import { authApi } from "../../api";
import type { CreateMasterTokenResponse } from "../../types/auth/Auth.types";

// 마스터 토큰 발급 API
const createMasterToken = async (): Promise<CreateMasterTokenResponse> => {
  const { data } = await authApi.post<CreateMasterTokenResponse>(
    "/api/v1/auth/test-login",
  );

  return data;
};

export default createMasterToken;
