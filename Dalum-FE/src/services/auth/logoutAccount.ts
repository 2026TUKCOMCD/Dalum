import { authApi } from "../../api";
import type { LogoutAccountResponse } from "../../types/auth/Auth.types";

// 로그아웃 API
const logoutAccount = async (): Promise<LogoutAccountResponse> => {
  const { data } = await authApi.post<LogoutAccountResponse>(
    "/api/v1/auth/logout",
  );

  return data;
};

export default logoutAccount;
