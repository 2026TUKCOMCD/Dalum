import { authApi } from '../../api';
import type { WithdrawAccountResponse } from '../../types/auth/Auth.types';

// 회원탈퇴 API
const withdrawAccount = async (): Promise<WithdrawAccountResponse> => {
  const { data } = await authApi.delete<WithdrawAccountResponse>(
    '/api/v1/auth/withdraw'
  );

  return data;
};

export default withdrawAccount;
