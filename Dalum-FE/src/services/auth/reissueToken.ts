import { authApi } from '../../api';
import type { ReissueTokenResponse } from '../../types/auth/Auth.types';

// 엑세스 토큰 재발급 API
const reissueToken = async (): Promise<ReissueTokenResponse> => {
  const { data } = await authApi.post<ReissueTokenResponse>(
    '/api/v1/auth/reissue'
  );

  return data;
};

export default reissueToken;
